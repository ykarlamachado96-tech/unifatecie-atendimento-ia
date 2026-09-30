from django.conf import settings
from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Aberto"
        AI_PROCESSING = "AI_PROCESSING", "IA processando"
        AI_WAITING_USER = "AI_WAITING_USER", "Aguardando aluno"
        WAITING_HUMAN = "WAITING_HUMAN", "Aguardando monitor"
        HUMAN_ASSIGNED = "HUMAN_ASSIGNED", "Monitor designado"
        HUMAN_PROCESSING = "HUMAN_PROCESSING", "Em atendimento humano"
        RESOLVED = "RESOLVED", "Resolvido"
        CLOSED = "CLOSED", "Encerrado"

    class ResolvedBy(models.TextChoices):
        AI = "AI", "IA"
        HUMAN = "HUMAN", "Humano"

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    intent = models.CharField(max_length=100, blank=True)
    handoff_context = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_monitor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_tickets",
    )
    resolved_by = models.CharField(max_length=10, choices=ResolvedBy.choices, null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket #{self.pk} - {self.student} ({self.status})"


class Message(models.Model):
    class SenderType(models.TextChoices):
        STUDENT = "STUDENT", "Aluno"
        MONITOR = "MONITOR", "Monitor"
        AI = "AI", "IA"
        SYSTEM = "SYSTEM", "Sistema"

    class ModerationStatus(models.TextChoices):
        CLEAN = "CLEAN", "Sem restrição"
        MASKED = "MASKED", "Mascarada"
        BLOCKED = "BLOCKED", "Bloqueada"

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_messages"
    )
    sender_type = models.CharField(max_length=10, choices=SenderType.choices)
    original_content = models.TextField()
    displayed_content = models.TextField()
    moderation_status = models.CharField(
        max_length=10, choices=ModerationStatus.choices, default=ModerationStatus.CLEAN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.sender_type}] {self.displayed_content[:40]}"
