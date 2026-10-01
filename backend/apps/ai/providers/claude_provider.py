import json

import anthropic
from django.conf import settings

from .base import AIProvider, ProviderError

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "cooperation": {"type": "integer"},
        "clarity": {"type": "integer"},
        "respectfulness": {"type": "integer"},
        "warnings": {"type": "integer"},
        "overall_score": {"type": "integer"},
        "justification": {"type": "string"},
    },
    "required": ["cooperation", "clarity", "respectfulness", "warnings", "overall_score", "justification"],
    "additionalProperties": False,
}


class ClaudeProvider(AIProvider):
    """Provider via API da Anthropic (documento, seção 10 — outro provider de IA plugável)."""

    name = "claude"

    def __init__(self, *, api_key=None, model_name=None, base_url=None, temperature=None, max_tokens=None):
        self.model_name = model_name or settings.CLAUDE_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens or 1024
        self._api_key = api_key or settings.ANTHROPIC_API_KEY
        self._client = None

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            if not self._api_key:
                raise ProviderError("ANTHROPIC_API_KEY não configurada.")
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def _create(self, *, system, user_content, schema=None, max_tokens=None):
        client = self._get_client()
        kwargs = {}
        if schema is not None:
            kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        try:
            response = client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens or self.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_content}],
                **kwargs,
            )
        except Exception as exc:  # noqa: BLE001 - qualquer falha do provider vira ProviderError
            raise ProviderError(f"Falha ao consultar Claude: {exc}") from exc

        if response.stop_reason == "refusal":
            raise ProviderError("Claude recusou a resposta por política de segurança.")

        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise ProviderError("Claude não retornou um bloco de texto.")
        return text

    def decide(self, *, system_prompt, history, user_message):
        # tool_args varia de formato por ferramenta, então não dá pra expressar num
        # json_schema estrito (a API exige additionalProperties=false em todo objeto
        # aninhado) — pedimos o JSON via instrução de prompt, como os outros providers.
        history_text = _format_history(history)
        prompt = (
            f"Histórico da conversa:\n{history_text}\n\n"
            f"Nova mensagem do aluno: {user_message}\n\n"
            "Responda SOMENTE com um JSON, sem texto adicional, no formato: "
            '{"intent": str, "confidence": float (0-1), "requires_tool": bool, '
            '"tool": str|null, "tool_args": object, "requires_human": bool, "reason": str|null, '
            '"setor": str|null, "assunto": str|null, "resumo": str|null}'
        )
        text = self._create(system=system_prompt, user_content=prompt)
        json.loads(_extract_json(text))  # valida antes de devolver ao harness
        return _extract_json(text)

    def compose_answer(self, *, system_prompt, decision, tool_result, history):
        history_text = _format_history(history)
        prompt = (
            f"Histórico da conversa:\n{history_text}\n\n"
            f"Intenção identificada: {decision.get('intent')}\n"
            f"Dados consultados: {json.dumps(tool_result, ensure_ascii=False) if tool_result else 'nenhum'}\n"
            f"Instrução interna (não mostrar ao aluno): {decision.get('reason') or 'nenhuma'}\n\n"
            "Escreva uma resposta curta, clara e cordial em português para o aluno, "
            "baseada exclusivamente nos dados consultados. Não invente informações."
        )
        return self._create(system=system_prompt, user_content=prompt).strip()

    def embed(self, text: str) -> list[float]:
        raise ProviderError(
            "ClaudeProvider não oferece embeddings; o RAG cai automaticamente para busca textual."
        )

    def score_conversation(self, transcript: str) -> str:
        system = (
            "Avalie o comportamento do aluno na conversa abaixo, com base exclusivamente "
            "no que foi registrado."
        )
        text = self._create(
            system=system, user_content=f"Conversa:\n{transcript}", schema=SCORE_SCHEMA,
        )
        json.loads(text)
        return text


def _format_history(history: list[dict]) -> str:
    return "\n".join(f"[{m['sender_type']}] {m['content']}" for m in history) or "(sem histórico anterior)"


def _extract_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
    return text.strip()
