from django.db import models
from pgvector.django import VectorField

EMBEDDING_DIM = 768


class AIExecution(models.Model):
    ticket = models.ForeignKey("support.Ticket", on_delete=models.CASCADE, related_name="ai_executions")
    message = models.ForeignKey(
        "support.Message", on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_executions"
    )
    provider = models.CharField(max_length=30, default="gemini")
    model = models.CharField(max_length=60, blank=True)
    prompt_version = models.CharField(max_length=30, blank=True)
    intent = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(default=0.0)
    tool = models.CharField(max_length=100, blank=True)
    input = models.JSONField(null=True, blank=True)
    output = models.JSONField(null=True, blank=True)
    latency_ms = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"AIExecution #{self.pk} - {self.intent} ({self.confidence:.2f})"


class ConversationScore(models.Model):
    """Score da IA para o aluno ao final do atendimento (documento, seção 19)."""

    ticket = models.OneToOneField("support.Ticket", on_delete=models.CASCADE, related_name="conversation_score")
    provider = models.CharField(max_length=30, default="gemini")
    model = models.CharField(max_length=60, blank=True)
    prompt_version = models.CharField(max_length=30, blank=True)
    cooperation = models.PositiveSmallIntegerField(default=0)
    clarity = models.PositiveSmallIntegerField(default=0)
    respectfulness = models.PositiveSmallIntegerField(default=0)
    warnings = models.PositiveSmallIntegerField(default=0)
    overall_score = models.PositiveSmallIntegerField(default=0)
    justification = models.TextField(blank=True)
    considered_message_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score ticket #{self.ticket_id} - {self.overall_score}"


class KnowledgeDocument(models.Model):
    class Category(models.TextChoices):
        REGULATION = "REGULATION", "Regulamento"
        FAQ = "FAQ", "FAQ"
        PROCEDURE = "PROCEDURE", "Procedimento"
        INTERNSHIP_RULES = "INTERNSHIP_RULES", "Regras de estágio"
        FINANCIAL_GUIDANCE = "FINANCIAL_GUIDANCE", "Orientação financeira"

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices)

    def __str__(self):
        return self.title


class KnowledgeChunk(models.Model):
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True)

    def __str__(self):
        return f"{self.document.title} [{self.pk}]"
