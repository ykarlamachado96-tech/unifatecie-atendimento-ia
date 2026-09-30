from .models import ConversationScore
from .prompts import PROMPT_VERSION
from .providers import ProviderError, get_provider
from .schemas import ConversationScoreOutput, ValidationError


def score_ticket_conversation(ticket):
    """Gera o score comportamental da IA para o aluno ao final do atendimento (seção 19).

    Falha silenciosamente (retorna None) se o provider não estiver disponível —
    a ausência do score não deve impedir o encerramento do atendimento.
    """
    if hasattr(ticket, "conversation_score"):
        return ticket.conversation_score

    messages = ticket.messages.order_by("created_at")
    if not messages.exists():
        return None
    transcript = "\n".join(f"[{m.sender_type}] {m.displayed_content}" for m in messages)

    provider = get_provider()
    try:
        raw = provider.score_conversation(transcript)
        data = ConversationScoreOutput.model_validate_json(raw)
    except (ProviderError, ValidationError, ValueError):
        return None

    return ConversationScore.objects.create(
        ticket=ticket, provider=provider.name, model=provider.model_name, prompt_version=PROMPT_VERSION,
        cooperation=data.cooperation, clarity=data.clarity, respectfulness=data.respectfulness,
        warnings=data.warnings, overall_score=data.overall_score, justification=data.justification,
        considered_message_ids=list(messages.values_list("id", flat=True)),
    )
