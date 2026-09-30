from django.db import models


class FinancialRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Aberto"
        PAID = "PAID", "Pago"
        OVERDUE = "OVERDUE", "Vencido"
        PROCESSING = "PROCESSING", "Pagamento não compensado"

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="financial_records"
    )
    reference_month = models.DateField(help_text="Primeiro dia do mês de referência")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-reference_month"]

    def __str__(self):
        return f"{self.student} - {self.reference_month:%m/%Y} ({self.status})"
