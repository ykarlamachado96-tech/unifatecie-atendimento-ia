from datetime import timedelta

from django.utils import timezone

from apps.evaluations.models import Evaluation
from apps.evaluations.tasks import apply_evaluation_timeouts


def test_pending_evaluation_past_deadline_gets_auto_timeout(make_ticket, student):
    ticket = make_ticket(student)
    evaluation = Evaluation.objects.create(
        ticket=ticket, student=student, status=Evaluation.Status.PENDING,
        deadline_at=timezone.now() - timedelta(hours=1),
    )

    count = apply_evaluation_timeouts()

    evaluation.refresh_from_db()
    assert count == 1
    assert evaluation.status == Evaluation.Status.AUTO_TIMEOUT
    assert evaluation.stars == 5
    assert evaluation.submitted_at is not None


def test_pending_evaluation_within_window_is_untouched(make_ticket, student):
    ticket = make_ticket(student)
    evaluation = Evaluation.objects.create(
        ticket=ticket, student=student, status=Evaluation.Status.PENDING,
        deadline_at=timezone.now() + timedelta(hours=23),
    )

    apply_evaluation_timeouts()

    evaluation.refresh_from_db()
    assert evaluation.status == Evaluation.Status.PENDING
    assert evaluation.stars is None


def test_already_submitted_evaluation_is_never_touched(make_ticket, student):
    ticket = make_ticket(student)
    evaluation = Evaluation.objects.create(
        ticket=ticket, student=student, status=Evaluation.Status.SUBMITTED, stars=3,
        deadline_at=timezone.now() - timedelta(hours=1), submitted_at=timezone.now(),
    )

    apply_evaluation_timeouts()

    evaluation.refresh_from_db()
    assert evaluation.status == Evaluation.Status.SUBMITTED
    assert evaluation.stars == 3
