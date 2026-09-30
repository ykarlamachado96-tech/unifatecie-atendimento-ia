import json

import requests
from django.conf import settings

from .base import AIProvider, ProviderError

EMBEDDING_MODEL = "nomic-embed-text"


def _extract_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
    return text.strip()


class LocalProvider(AIProvider):
    """Provider local via Ollama (documento, seção 10) — útil para desenvolver/testar
    sem consumir a cota limitada de APIs externas."""

    name = "local"

    def __init__(self):
        self.model_name = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL

    def _generate(self, prompt: str, json_mode: bool = False) -> str:
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        if json_mode:
            payload["format"] = "json"
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=180)
            resp.raise_for_status()
            return resp.json()["response"]
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Falha ao consultar Ollama: {exc}") from exc

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
        raw = _extract_json(self._generate(prompt, json_mode=True))
        try:
            json.loads(raw)
        except ValueError as exc:
            raise ProviderError(f"Ollama não retornou JSON válido: {raw[:200]}") from exc
        return raw

    def compose_answer(self, *, system_prompt, decision, tool_result, history):
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
        return self._generate(prompt).strip()

    def embed(self, text: str) -> list[float]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["embedding"]
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Falha ao gerar embedding local: {exc}") from exc

    def score_conversation(self, transcript: str) -> str:
        prompt = (
            "Avalie o comportamento do aluno na conversa abaixo, com base exclusivamente "
            "no que foi registrado. Responda SOMENTE com um JSON no formato: "
            '{"cooperation": int (0-100), "clarity": int (0-100), "respectfulness": int (0-100), '
            '"warnings": int, "overall_score": int (0-100), "justification": str}\n\n'
            f"Conversa:\n{transcript}"
        )
        raw = _extract_json(self._generate(prompt, json_mode=True))
        try:
            json.loads(raw)
        except ValueError as exc:
            raise ProviderError(f"Ollama não retornou JSON válido: {raw[:200]}") from exc
        return raw


def _format_history(history: list[dict]) -> str:
    return "\n".join(f"[{m['sender_type']}] {m['content']}" for m in history) or "(sem histórico anterior)"
