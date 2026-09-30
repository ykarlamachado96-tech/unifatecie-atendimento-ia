from django.conf import settings
from django.db import models


class Occurrence(models.Model):
    class Category(models.TextChoices):
        PROFANITY = "PROFANITY", "Palavrão"
        INSULT = "INSULT", "Insulto"
        THREAT = "THREAT", "Ameaça"
        DISCRIMINATION = "DISCRIMINATION", "Discriminação"
        HARASSMENT = "HARASSMENT", "Assédio"

    class Severity(models.TextChoices):
        LOW = "LOW", "Leve"
        MEDIUM = "MEDIUM", "Média"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Aluno"
        MONITOR = "MONITOR", "Monitor"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="occurrences")
    role = models.CharField(max_length=10, choices=Role.choices)
    ticket = models.ForeignKey("support.Ticket", on_delete=models.CASCADE, related_name="occurrences")
    message = models.ForeignKey("support.Message", on_delete=models.CASCADE, related_name="occurrences")
    category = models.CharField(max_length=20, choices=Category.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    original_message = models.TextField()
    sanitized_message = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    validator_version = models.CharField(max_length=30, default="regex-v1")

    class Meta:
        ordering = ["-detected_at"]

    def __str__(self):
        return f"{self.user} - {self.category} ({self.severity})"
