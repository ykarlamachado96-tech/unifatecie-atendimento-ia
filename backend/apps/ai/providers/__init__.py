from django.conf import settings

from .base import AIProvider, ProviderError
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .local_provider import LocalProvider

_provider_instance: AIProvider | None = None

_PROVIDER_CLASSES = {
    "local": LocalProvider,
    "gemini": GeminiProvider,
    "claude": ClaudeProvider,
}


def get_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is None:
        provider_cls = _PROVIDER_CLASSES.get(settings.AI_PROVIDER, GeminiProvider)
        _provider_instance = provider_cls()
    return _provider_instance


__all__ = ["AIProvider", "ProviderError", "GeminiProvider", "LocalProvider", "ClaudeProvider", "get_provider"]
