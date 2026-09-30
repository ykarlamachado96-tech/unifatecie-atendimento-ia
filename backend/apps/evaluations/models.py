from django.conf import settings
from django.db import models


class Evaluation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        SUBMITTED = "SUBMITTED", "Avaliado pelo aluno"
        AUTO_TIMEOUT = "AUTO_TIMEOUT", "Nota automática (timeout)"

    ticket = models.OneToOneField("support.Ticket", on_delete=models.CASCADE, related_name="evaluation")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="evaluations")
    monitor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_evaluations"
    )
    stars = models.PositiveSmallIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Avaliação ticket #{self.ticket_id} - {self.status}"
