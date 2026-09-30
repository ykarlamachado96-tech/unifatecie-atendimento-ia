from django.utils import timezone


def create_support_ticket(student, **kwargs):
    from apps.support.models import Ticket

    ticket = Ticket.objects.create(student=student)
    return {"ticket_id": ticket.id, "status": ticket.status}


def transfer_to_human(student, ticket=None, reason=None, **kwargs):
    if ticket is None:
        return {"error": "ticket é obrigatório"}
    from apps.support.models import Ticket

    ticket.status = Ticket.Status.WAITING_HUMAN
    ticket.save(update_fields=["status"])
    return {"ticket_id": ticket.id, "status": ticket.status, "reason": reason}


def get_ticket_status(student, ticket=None, **kwargs):
    if ticket is None:
        return {"error": "ticket é obrigatório"}
    return {"ticket_id": ticket.id, "status": ticket.status}


def close_ticket(student, ticket=None, **kwargs):
    if ticket is None:
        return {"error": "ticket é obrigatório"}
    from apps.support.models import Ticket

    ticket.status = Ticket.Status.CLOSED
    ticket.closed_at = timezone.now()
    ticket.save(update_fields=["status", "closed_at"])
    return {"ticket_id": ticket.id, "status": ticket.status}
