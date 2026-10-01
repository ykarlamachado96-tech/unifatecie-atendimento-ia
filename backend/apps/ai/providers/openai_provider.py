import json

import openai

from .base import AIProvider, ProviderError

EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_MODEL = "gpt-4o-mini"


def _extract_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
    return text.strip()


class OpenAIProvider(AIProvider):
    """Provider via API da OpenAI (ChatGPT)."""

    name = "openai"

    def __init__(self, *, api_key=None, model_name=None, base_url=None, temperature=None, max_tokens=None):
        self.model_name = model_name or DEFAULT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens or 1024
        self._api_key = api_key
        self._client = None

    def _get_client(self) -> openai.OpenAI:
        if self._client is None:
            if not self._api_key:
                raise ProviderError("Chave de API da OpenAI não configurada.")
            self._client = openai.OpenAI(api_key=self._api_key)
        return self._client

    def _chat(self, *, system: str, user_content: str, json_mode: bool = False) -> str:
        client = self._get_client()
        kwargs = {}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user_content}],
                **kwargs,
            )
        except Exception as exc:  # noqa: BLE001 - qualquer falha do provider vira ProviderError
            raise ProviderError(f"Falha ao consultar OpenAI: {exc}") from exc

        text = response.choices[0].message.content
        if text is None:
            raise ProviderError("OpenAI não retornou conteúdo de texto.")
        return text

    def decide(self, *, system_prompt, history, user_message):
        history_text = _format_history(history)
        prompt = (
            f"Histórico da conversa:\n{history_text}\n\n"
            f"Nova mensagem do aluno: {user_message}\n\n"
            "Responda SOMENTE com um JSON, sem texto adicional, no formato: "
            '{"intent": str, "confidence": float (0-1), "requires_tool": bool, '
            '"tool": str|null, "tool_args": object, "requires_human": bool, "reason": str|null, '
            '"setor": str|null, "assunto": str|null, "resumo": str|null}'
        )
        text = self._chat(system=system_prompt, user_content=prompt, json_mode=True)
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
        return self._chat(system=system_prompt, user_content=prompt).strip()

    def embed(self, text: str) -> list[float]:
        client = self._get_client()
        try:
            response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Falha ao gerar embedding na OpenAI: {exc}") from exc
        return response.data[0].embedding

    def score_conversation(self, transcript: str) -> str:
        system = (
            "Avalie o comportamento do aluno na conversa abaixo, com base exclusivamente "
            "no que foi registrado."
        )
        text = self._chat(
            system=system,
            user_content=(
                "Responda SOMENTE com um JSON no formato: "
                '{"cooperation": int (0-100), "clarity": int (0-100), "respectfulness": int (0-100), '
                '"warnings": int, "overall_score": int (0-100), "justification": str}\n\n'
                f"Conversa:\n{transcript}"
            ),
            json_mode=True,
        )
        json.loads(_extract_json(text))
        return _extract_json(text)


def _format_history(history: list[dict]) -> str:
    return "\n".join(f"[{m['sender_type']}] {m['content']}" for m in history) or "(sem histórico anterior)"
