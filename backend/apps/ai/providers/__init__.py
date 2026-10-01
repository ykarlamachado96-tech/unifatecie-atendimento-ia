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


def _active_credential():
    """Credencial marcada como ativa no Django Admin, se existir — permite trocar provider/chave
    pela aplicação sem editar .env. Falha silenciosamente antes das migrations existirem."""
    from apps.ai.models import AIProviderCredential

    try:
        return AIProviderCredential.objects.filter(is_active=True).first()
    except Exception:  # noqa: BLE001 - tabela ainda não migrada, banco indisponível etc.
        return None


def _build_provider() -> AIProvider:
    credential = _active_credential()
    if credential is not None:
        provider_cls = _PROVIDER_CLASSES.get(credential.provider)
        if provider_cls is not None:
            return provider_cls(
                api_key=credential.api_key or None,
                model_name=credential.model_name or None,
                base_url=credential.base_url or None,
                temperature=credential.temperature,
                max_tokens=credential.max_tokens,
            )

    provider_cls = _PROVIDER_CLASSES.get(settings.AI_PROVIDER, GeminiProvider)
    return provider_cls()


def get_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = _build_provider()
    return _provider_instance


__all__ = [
    "AIProvider", "ProviderError", "GeminiProvider", "LocalProvider", "ClaudeProvider", "OpenAIProvider",
    "get_provider",
]
