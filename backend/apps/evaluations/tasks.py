from celery import shared_task
from django.utils import timezone

from .models import Evaluation


@shared_task
def apply_evaluation_timeouts():
    """Regra das 24h (documento, seção 22): avaliação não enviada vira nota automática 5."""
    pending = Evaluation.objects.filter(status=Evaluation.Status.PENDING, deadline_at__lte=timezone.now())
    count = pending.update(status=Evaluation.Status.AUTO_TIMEOUT, stars=5, submitted_at=timezone.now())
    return count
