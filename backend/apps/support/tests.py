from rest_framework.test import APIClient

from apps.support.models import Ticket


def _client_as(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_student_list_only_shows_own_tickets(make_student, make_ticket):
    alice = make_student(ra="FTC900001")
    bob = make_student(ra="FTC900002")
    make_ticket(alice)
    bob_ticket = make_ticket(bob)

    response = _client_as(bob.user).get("/api/support/tickets/")

    assert response.status_code == 200
    ids = [t["id"] for t in response.data]
    assert ids == [bob_ticket.id]


def test_student_cannot_fetch_another_students_ticket_detail(make_student, make_ticket):
    alice = make_student(ra="FTC900003")
    bob = make_student(ra="FTC900004")
    alice_ticket = make_ticket(alice)

    response = _client_as(bob.user).get(f"/api/support/tickets/{alice_ticket.id}/")

    assert response.status_code == 404


def test_monitor_queue_only_shows_waiting_human_tickets(make_student, make_ticket, monitor_user):
    student = make_student(ra="FTC900005")
    waiting = make_ticket(student, status=Ticket.Status.WAITING_HUMAN)
    make_ticket(student, status=Ticket.Status.OPEN)

    response = _client_as(monitor_user).get("/api/support/tickets/queue/")

    assert response.status_code == 200
    ids = [t["id"] for t in response.data]
    assert ids == [waiting.id]


def test_only_student_can_create_ticket(monitor_user):
    response = _client_as(monitor_user).post("/api/support/tickets/")
    assert response.status_code == 403
