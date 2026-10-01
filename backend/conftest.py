import pytest
from django.contrib.auth import get_user_model

from apps.academic.models import Course
from apps.students.models import Student
from apps.support.models import Ticket

User = get_user_model()


@pytest.fixture
def course(db):
    return Course.objects.create(name="Pedagogia", code="PED", total_periods=8, internship_eligible_period=7)


@pytest.fixture
def make_student(db, course):
    def _make(ra="FTC900000", period=7, **kwargs):
        user = User.objects.create_user(username=ra, password=ra, role=User.Role.STUDENT)
        return Student.objects.create(user=user, ra=ra, course=course, current_period=period, **kwargs)

    return _make


@pytest.fixture
def student(make_student):
    return make_student()


@pytest.fixture
def monitor_user(db):
    return User.objects.create_user(username="atendente.teste", password="demo123", role=User.Role.MONITOR)


@pytest.fixture
def make_ticket(db):
    def _make(student, **kwargs):
        return Ticket.objects.create(student=student, **kwargs)

    return _make
