from pydantic import BaseModel, Field, ValidationError, field_validator

__all__ = ["IntentDecision", "ValidationError", "ConversationScoreOutput"]


class IntentDecision(BaseModel):
    """Saída estruturada da IA (documento, seção 11), validada antes de qualquer ação."""

    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    requires_tool: bool = False
    tool: str | None = None
    tool_args: dict = Field(default_factory=dict)
    requires_human: bool = False
    reason: str | None = None
    setor: str | None = None
    assunto: str | None = None
    resumo: str | None = None

    @field_validator("tool_args", mode="before")
    @classmethod
    def _default_none_tool_args(cls, value):
        # alguns modelos (sobretudo locais/menores) retornam null em vez de {}
        return value if value is not None else {}


class ConversationScoreOutput(BaseModel):
    """Score da IA para o aluno ao final do atendimento (documento, seção 19)."""

    cooperation: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    respectfulness: int = Field(ge=0, le=100)
    warnings: int = Field(ge=0)
    overall_score: int = Field(ge=0, le=100)
    justification: str = ""
