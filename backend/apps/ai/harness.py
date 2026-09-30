import json
import time

from apps.support.models import Message, Ticket
from apps.moderation import service as moderation_service

from .models import AIExecution
from .prompts import PROMPT_VERSION, RESPONDER_SYSTEM_PROMPT, ROUTER_SYSTEM_PROMPT
from .providers import ProviderError, get_provider
from .schemas import IntentDecision, ValidationError
from .tools import TOOL_REGISTRY

CONFIDENCE_THRESHOLD = 0.6

HUMAN_STATES = (Ticket.Status.WAITING_HUMAN, Ticket.Status.HUMAN_ASSIGNED, Ticket.Status.HUMAN_PROCESSING)


def handle_incoming_message(*, ticket: Ticket, raw_text: str, sender_user) -> Message:
    role = getattr(sender_user, "role", None)
    sender_type = role if role in (Message.SenderType.STUDENT, Message.SenderType.MONITOR) else Message.SenderType.SYSTEM

    mod_result = moderation_service.check(raw_text)
    message = Message.objects.create(
        ticket=ticket, sender=sender_user, sender_type=sender_type,
        original_content=raw_text, displayed_content=mod_result.sanitized_text,
        moderation_status=mod_result.status,
    )

    if mod_result.flagged:
        moderation_service.register_occurrence(
            user=sender_user, role=sender_type, ticket=ticket, message=message, result=mod_result,
        )
        if mod_result.status == "BLOCKED":
            _emit_system_message(ticket, "Sua mensagem foi bloqueada por conteúdo inadequado.")
            return message

    if ticket.status in HUMAN_STATES:
        return message

    if sender_type != Message.SenderType.STUDENT:
        return message

    _run_ai_turn(ticket, message)
    return message


def _run_ai_turn(ticket: Ticket, message: Message) -> None:
    ticket.status = Ticket.Status.AI_PROCESSING
    ticket.save(update_fields=["status"])

    provider = get_provider()
    history = _build_history(ticket)

    decision, ai_execution = _decide(ticket, message, provider, history)

    tool_result = None
    if decision and decision.requires_tool and decision.tool in TOOL_REGISTRY:
        tool_fn = TOOL_REGISTRY[decision.tool]
        try:
            tool_result = tool_fn(student=ticket.student, ticket=ticket, **decision.tool_args)
        except Exception as exc:  # noqa: BLE001 - erro de ferramenta não deve derrubar o atendimento
            tool_result = {"error": str(exc)}
        ai_execution.output = tool_result
        ai_execution.save(update_fields=["output"])

    # Confiança baixa só força handoff quando uma ferramenta foi de fato escolhida
    # (a escolha pode estar errada). Uma pergunta de esclarecimento (sem ferramenta)
    # pode ter confiança baixa por natureza e não deve ser tratada como falha.
    low_confidence_tool_call = bool(decision and decision.requires_tool and decision.confidence < CONFIDENCE_THRESHOLD)

    if decision is None or decision.requires_human or low_confidence_tool_call:
        reason = decision.reason if decision else "Falha ao processar a mensagem com a IA."
        _handoff_to_human(ticket, decision, tool_result, reason)
        return

    try:
        answer = provider.compose_answer(
            system_prompt=RESPONDER_SYSTEM_PROMPT, decision=decision.model_dump(), tool_result=tool_result, history=history,
        )
    except ProviderError as exc:
        _handoff_to_human(ticket, decision, tool_result, f"Falha ao compor resposta: {exc}")
        return

    answer = _sanitize_answer_text(answer)

    if _looks_like_unfulfillable_promise(answer):
        _handoff_to_human(
            ticket, decision, tool_result,
            "A IA não conseguiu responder com dados concretos e ia prometer um retorno "
            "futuro que o sistema não realiza automaticamente — encaminhado por segurança.",
        )
        return

    Message.objects.create(
        ticket=ticket, sender=None, sender_type=Message.SenderType.AI,
        original_content=answer, displayed_content=answer, moderation_status=Message.ModerationStatus.CLEAN,
    )
    ticket.status = Ticket.Status.AI_WAITING_USER
    ticket.intent = decision.intent
    ticket.save(update_fields=["status", "intent"])


def _decide(ticket, message, provider, history):
    started = time.monotonic()
    ai_execution = AIExecution.objects.create(
        ticket=ticket, message=message, provider=provider.name, model=provider.model_name,
        prompt_version=PROMPT_VERSION,
    )
    try:
        raw = provider.decide(system_prompt=ROUTER_SYSTEM_PROMPT, history=history, user_message=message.displayed_content)
        decision = IntentDecision.model_validate_json(raw)
    except (ProviderError, ValidationError, ValueError) as exc:
        ai_execution.error = str(exc)
        ai_execution.latency_ms = int((time.monotonic() - started) * 1000)
        ai_execution.save(update_fields=["error", "latency_ms"])
        return None, ai_execution

    ai_execution.intent = decision.intent
    ai_execution.confidence = decision.confidence
    ai_execution.tool = decision.tool or ""
    ai_execution.input = decision.tool_args
    ai_execution.latency_ms = int((time.monotonic() - started) * 1000)
    ai_execution.save(update_fields=["intent", "confidence", "tool", "input", "latency_ms"])
    return decision, ai_execution


def _handoff_to_human(ticket, decision, tool_result, reason):
    ticket.status = Ticket.Status.WAITING_HUMAN
    if decision:
        ticket.intent = decision.intent
    ticket.handoff_context = _build_handoff_context(ticket, decision, tool_result, reason)
    ticket.save(update_fields=["status", "intent", "handoff_context"])
    _emit_system_message(ticket, f"Encaminhado para atendimento humano: {reason}")


def _build_handoff_context(ticket, decision, tool_result, reason):
    history = _build_history(ticket)
    return {
        "setor": decision.setor if decision else None,
        "assunto": decision.assunto if decision else None,
        "resumo": decision.resumo if decision else (history[-1]["content"] if history else ""),
        "summary": history[-1]["content"] if history else "",
        "intent": decision.intent if decision else None,
        "tools_used": [decision.tool] if decision and decision.tool else [],
        "data_consulted": tool_result,
        "reason": reason,
        "suggested_next_step": "Revisar o contexto acima e responder diretamente ao aluno.",
    }


def _emit_system_message(ticket, text):
    Message.objects.create(
        ticket=ticket, sender=None, sender_type=Message.SenderType.SYSTEM,
        original_content=text, displayed_content=text, moderation_status=Message.ModerationStatus.CLEAN,
    )


def _sanitize_answer_text(text: str) -> str:
    """Rede de segurança: se o provider vazar JSON/markdown na resposta final
    (em vez de texto natural), tenta extrair só o texto para o aluno."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped[:4].lower() == "json":
            stripped = stripped[4:]
        stripped = stripped.strip()

    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            data = json.loads(stripped)
        except ValueError:
            return text.strip()
        if isinstance(data, dict):
            for key in ("response", "answer", "message", "text", "reply"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return text.strip()

    return text.strip()


EMPTY_PROMISE_MARKERS = (
    "vou verificar", "vou checar", "vou consultar isso", "vou confirmar e",
    "entrarei em contato", "entraremos em contato", "assim que possível",
    "retorno em breve", "retorno assim que", "verificar com o setor",
    "verificar com a equipe", "te aviso assim que", "aviso assim que",
)


def _looks_like_unfulfillable_promise(text: str) -> bool:
    """Rede de segurança: a IA só tem uma resposta por mensagem — se o texto promete
    um retorno futuro que o sistema não sustenta, é melhor encaminhar de verdade
    para um humano do que deixar o aluno esperando algo que nunca vai chegar."""
    lowered = text.lower()
    return any(marker in lowered for marker in EMPTY_PROMISE_MARKERS)


def _build_history(ticket, limit=20):
    messages = ticket.messages.order_by("-created_at")[:limit]
    return [
        {"sender_type": m.sender_type, "content": m.displayed_content}
        for m in reversed(list(messages))
    ]
