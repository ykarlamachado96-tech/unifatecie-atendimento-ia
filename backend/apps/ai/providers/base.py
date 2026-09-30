from abc import ABC, abstractmethod


class ProviderError(Exception):
    """Erro de comunicação ou resposta inválida do provider de IA."""


class AIProvider(ABC):
    """Interface abstrata de provider de IA (documento, seção 10).

    Implementações possíveis: GeminiProvider (MVP), OpenAIProvider, LocalProvider.
    """

    name: str
    model_name: str

    @abstractmethod
    def decide(self, *, system_prompt: str, history: list[dict], user_message: str) -> str:
        """Retorna a saída estruturada da IA como string JSON (documento, seção 11)."""

    @abstractmethod
    def compose_answer(self, *, system_prompt: str, decision: dict, tool_result: dict | None, history: list[dict]) -> str:
        """Gera a resposta final em linguagem natural para o aluno."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Gera o embedding de um texto para uso no RAG (pgvector)."""

    @abstractmethod
    def score_conversation(self, transcript: str) -> str:
        """Retorna a análise comportamental da conversa como string JSON (seção 19)."""
