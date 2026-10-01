import json

import pytest

from apps.ai.harness import (
    _looks_like_unfulfillable_promise,
    _sanitize_answer_text,
    handle_incoming_message,
)
from apps.support.models import Message, Ticket


class FakeProvider:
    """Stub de AIProvider — permite testar a orquestração do harness sem chamar uma API real."""

    name = "fake"
    model_name = "fake-model"

    def __init__(self, decision: dict, answer: str = "Resposta de teste."):
        self._decision = decision
        self._answer = answer

    def decide(self, *, system_prompt, history, user_message):
        return json.dumps(self._decision)

    def compose_answer(self, *, system_prompt, decision, tool_result, history):
        return self._answer

    def embed(self, text):
        raise NotImplementedError

    def score_conversation(self, transcript):
        raise NotImplementedError


@pytest.fixture
def ticket(make_ticket, student):
    return make_ticket(student)


def _patch_provider(monkeypatch, provider):
    monkeypatch.setattr("apps.ai.harness.get_provider", lambda: provider)


# ---- redes de segurança (funções puras) ----


def test_sanitize_extracts_text_from_leaked_json():
    leaked = '{"response": "Você não tem boletos em aberto."}'
    assert _sanitize_answer_text(leaked) == "Você não tem boletos em aberto."


def test_sanitize_strips_json_code_fence():
    leaked = '```json\n{"message": "Tudo certo por aqui."}\n```'
    assert _sanitize_answer_text(leaked) == "Tudo certo por aqui."


def test_sanitize_leaves_normal_text_untouched():
    text = "Sim, você já pode abrir a próxima etapa."
    assert _sanitize_answer_text(text) == text


def test_detects_unfulfillable_future_promise():
    assert _looks_like_unfulfillable_promise("Vou verificar e te aviso assim que possível.") is True


def test_normal_answer_is_not_flagged_as_promise():
    assert _looks_like_unfulfillable_promise("Sua dispensa está deferida em 50%, restam 48h.") is False


# ---- orquestração ponta a ponta (provider stub, sem API real) ----


def test_tool_call_with_high_confidence_resolves_and_answers(monkeypatch, ticket, student):
    decision = {
        "intent": "consulta_estagio", "confidence": 0.95, "requires_tool": True,
        "tool": "get_student_internship_status", "tool_args": {}, "requires_human": False,
        "reason": None, "setor": None, "assunto": None, "resumo": None,
    }
    _patch_provider(monkeypatch, FakeProvider(decision, answer="Você ainda não solicitou nenhuma etapa."))

    handle_incoming_message(ticket=ticket, raw_text="Já posso abrir a próxima etapa?", sender_user=student.user)

    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.AI_WAITING_USER
    assert ticket.intent == "consulta_estagio"
    last_message = ticket.messages.order_by("-created_at").first()
    assert last_message.sender_type == Message.SenderType.AI
    assert last_message.displayed_content == "Você ainda não solicitou nenhuma etapa."


def test_requires_human_triggers_handoff_with_context(monkeypatch, ticket, student):
    decision = {
        "intent": "caso_excepcional", "confidence": 0.9, "requires_tool": False, "tool": None,
        "tool_args": {}, "requires_human": True, "reason": "Exceção de política.",
        "setor": "Estágio", "assunto": "Caso excepcional", "resumo": "Resumo do problema do aluno.",
    }
    _patch_provider(monkeypatch, FakeProvider(decision))

    handle_incoming_message(ticket=ticket, raw_text="Minha situação é muito específica.", sender_user=student.user)

    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.WAITING_HUMAN
    assert ticket.handoff_context["setor"] == "Estágio"
    assert ticket.handoff_context["assunto"] == "Caso excepcional"
    assert ticket.handoff_context["reason"] == "Exceção de política."


def test_low_confidence_tool_call_triggers_handoff(monkeypatch, ticket, student):
    decision = {
        "intent": "duvida_confusa", "confidence": 0.3, "requires_tool": True,
        "tool": "get_student_internship_status", "tool_args": {}, "requires_human": False,
        "reason": "Não tenho certeza da ferramenta certa.", "setor": "Estágio",
        "assunto": "dúvida", "resumo": "resumo",
    }
    _patch_provider(monkeypatch, FakeProvider(decision))

    handle_incoming_message(ticket=ticket, raw_text="sei lá, me ajuda", sender_user=student.user)

    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.WAITING_HUMAN


def test_blocked_moderation_never_reaches_ai(monkeypatch, ticket, student):
    def _fail():
        raise AssertionError("IA não deveria ser chamada para mensagem bloqueada por moderação")

    monkeypatch.setattr("apps.ai.harness.get_provider", _fail)

    handle_incoming_message(
        ticket=ticket, raw_text="Vou te matar se isso não for resolvido.", sender_user=student.user,
    )

    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.OPEN  # nunca chegou a processar com IA
    messages = list(ticket.messages.order_by("created_at"))
    assert messages[0].moderation_status == "BLOCKED"
    assert messages[-1].sender_type == Message.SenderType.SYSTEM
