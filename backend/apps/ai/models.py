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


class AIProviderCredential(models.Model):
    """Credencial de provider de IA configurável pela aplicação (Django Admin), com fallback
    para as variáveis de ambiente quando nenhuma credencial estiver marcada como ativa."""

    class Provider(models.TextChoices):
        OPENAI = "openai", "ChatGPT (OpenAI)"
        CLAUDE = "claude", "Claude (Anthropic)"
        GEMINI = "gemini", "Gemini (Google)"
        OLLAMA = "ollama", "Ollama (local)"

    provider = models.CharField(max_length=20, choices=Provider.choices, unique=True)
    api_key = models.CharField(max_length=300, blank=True)
    base_url = models.CharField(max_length=300, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False, help_text="Usado para classificar e responder o aluno.")
    use_for_embeddings = models.BooleanField(
        default=False, help_text="Usado só para gerar embeddings do RAG (busca na base de conhecimento)."
    )
    temperature = models.FloatField(null=True, blank=True)
    max_tokens = models.PositiveIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            AIProviderCredential.objects.exclude(pk=self.pk).update(is_active=False)
        if self.use_for_embeddings:
            AIProviderCredential.objects.exclude(pk=self.pk).update(use_for_embeddings=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_provider_display()} ({'ativo' if self.is_active else 'inativo'})"


class KnowledgeSource(models.Model):
    """Cadastro de uma fonte de conhecimento (upload ou texto colado) a ser processada e
    carregada em KnowledgeDocument/KnowledgeChunk — a "alimentação" da base de RAG pelo Admin,
    sem precisar de um comando de terminal."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Aguardando processamento"
        PROCESSED = "PROCESSED", "Processado"
        ERROR = "ERROR", "Erro no processamento"

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=KnowledgeDocument.Category.choices)
    file = models.FileField(upload_to="knowledge_sources/", blank=True, null=True)
    raw_text = models.TextField(blank=True, help_text="Alternativa a enviar um arquivo: cole o texto aqui.")
    document = models.ForeignKey(KnowledgeDocument, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.CharField(max_length=500, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
