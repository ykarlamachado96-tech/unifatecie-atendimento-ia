import json
import time

from django.conf import settings
from google import genai
from google.genai import types

from .base import AIProvider, ProviderError

EMBEDDING_MODEL = "text-embedding-004"

RETRYABLE_MARKERS = ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED")
RETRY_BACKOFF_SECONDS = (3, 6)  # tentativas extras além da primeira


def _is_retryable(exc: Exception) -> bool:
    text = str(exc)
    return any(marker in text for marker in RETRYABLE_MARKERS)


def _call_with_retry(func):
    """Chamadas ao Gemini sofrem picos de 429/503 em momentos de alta demanda —
    tenta algumas vezes com backoff antes de desistir e acionar o fallback do harness."""
    last_exc = None
    for delay in (0, *RETRY_BACKOFF_SECONDS):
        if delay:
            time.sleep(delay)
        try:
            return func()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if not _is_retryable(exc):
                raise ProviderError(f"Falha ao consultar Gemini: {exc}") from exc
    raise ProviderError(f"Falha ao consultar Gemini após múltiplas tentativas: {last_exc}") from last_exc


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, *, api_key=None, model_name=None, base_url=None, temperature=None, max_tokens=None):
        self.model_name = model_name or settings.GEMINI_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._client = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self._api_key or self._api_key == "changeme":
                raise ProviderError("GEMINI_API_KEY não configurada.")
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _generate_json(self, prompt: str) -> dict:
        client = self._get_client()

        def call():
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
            )
            return json.loads(response.text)

        return _call_with_retry(call)

    def decide(self, *, system_prompt, history, user_message):
        history_text = _format_history(history)
        prompt = (
            f"{system_prompt}\n\n"
            f"Histórico da conversa:\n{history_text}\n\n"
            f"Nova mensagem do aluno: {user_message}\n\n"
            "Responda SOMENTE com um JSON no formato: "
            '{"intent": str, "confidence": float (0-1), "requires_tool": bool, '
            '"tool": str|null, "tool_args": object, "requires_human": bool, "reason": str|null, '
            '"setor": str|null, "assunto": str|null, "resumo": str|null}'
        )
        data = self._generate_json(prompt)
        return json.dumps(data, ensure_ascii=False)

    def compose_answer(self, *, system_prompt, decision, tool_result, history):
        client = self._get_client()
        history_text = _format_history(history)
        prompt = (
            f"{system_prompt}\n\n"
            f"Histórico da conversa:\n{history_text}\n\n"
            f"Intenção identificada: {decision.get('intent')}\n"
            f"Dados consultados: {json.dumps(tool_result, ensure_ascii=False) if tool_result else 'nenhum'}\n"
            f"Instrução interna (não mostrar ao aluno): {decision.get('reason') or 'nenhuma'}\n\n"
            "Escreva uma resposta curta, clara e cordial em português para o aluno, "
            "baseada exclusivamente nos dados consultados. Não invente informações."
        )

        def call():
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature, max_output_tokens=self.max_tokens,
                ),
            )
            return response.text.strip()

        return _call_with_retry(call)

    def embed(self, text: str) -> list[float]:
        client = self._get_client()

        def call():
            result = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
            return result.embeddings[0].values

        return _call_with_retry(call)

    def score_conversation(self, transcript: str) -> str:
        prompt = (
            "Avalie o comportamento do aluno na conversa abaixo, com base exclusivamente "
            "no que foi registrado. Responda SOMENTE com um JSON no formato: "
            '{"cooperation": int (0-100), "clarity": int (0-100), "respectfulness": int (0-100), '
            '"warnings": int, "overall_score": int (0-100), "justification": str}\n\n'
            f"Conversa:\n{transcript}"
        )
        data = self._generate_json(prompt)
        return json.dumps(data, ensure_ascii=False)


def _format_history(history: list[dict]) -> str:
    return "\n".join(f"[{m['sender_type']}] {m['content']}" for m in history) or "(sem histórico anterior)"
