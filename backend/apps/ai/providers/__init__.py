from django.conf import settings

from .base import AIProvider, ProviderError
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .local_provider import LocalProvider
from .openai_provider import OpenAIProvider

_provider_instance: AIProvider | None = None

_PROVIDER_CLASSES = {
    "local": LocalProvider,
    "gemini": GeminiProvider,
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
}


def _credential(**filters):
    """Credencial marcada no Django Admin, se existir — permite configurar provider/chave pela
    aplicação sem editar .env. Falha silenciosamente antes das migrations existirem."""
    from apps.ai.models import AIProviderCredential

    try:
        return AIProviderCredential.objects.filter(**filters).first()
    except Exception:  # noqa: BLE001 - tabela ainda não migrada, banco indisponível etc.
        return None


def _instantiate(credential) -> AIProvider | None:
    provider_cls = _PROVIDER_CLASSES.get(credential.provider)
    if provider_cls is None:
        return None
    return provider_cls(
        api_key=credential.api_key or None,
        model_name=credential.model_name or None,
        base_url=credential.base_url or None,
        temperature=credential.temperature,
        max_tokens=credential.max_tokens,
    )


def _build_provider() -> AIProvider:
    credential = _credential(is_active=True)
    if credential is not None:
        instance = _instantiate(credential)
        if instance is not None:
            return instance

    provider_cls = _PROVIDER_CLASSES.get(settings.AI_PROVIDER, GeminiProvider)
    return provider_cls()


def get_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = _build_provider()
    return _provider_instance


def get_embedding_provider() -> AIProvider:
    """Provider usado só para apps/ai/ingestion.py e apps/ai/tools/knowledge.py (embedding do
    RAG) — pode ser diferente do provider de decisão/resposta (ex.: Claude não gera embedding,
    mas pode ser o provider ativo para decide()/compose_answer())."""
    credential = _credential(use_for_embeddings=True)
    if credential is not None:
        instance = _instantiate(credential)
        if instance is not None:
            return instance
    return get_provider()


__all__ = [
    "AIProvider", "ProviderError", "GeminiProvider", "LocalProvider", "ClaudeProvider", "OpenAIProvider",
    "get_provider", "get_embedding_provider",
]
