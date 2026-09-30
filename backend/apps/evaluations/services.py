from datetime import timedelta

from django.utils import timezone

from .models import Evaluation

EVALUATION_WINDOW_HOURS = 24


def create_pending_evaluation(ticket) -> Evaluation:
    if hasattr(ticket, "evaluation"):
        return ticket.evaluation
    return Evaluation.objects.create(
        ticket=ticket,
        student=ticket.student,
        monitor=ticket.assigned_monitor,
        status=Evaluation.Status.PENDING,
        deadline_at=timezone.now() + timedelta(hours=EVALUATION_WINDOW_HOURS),
    )
