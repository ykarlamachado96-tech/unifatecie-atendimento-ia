from django.contrib.auth import get_user_model

SANDBOX_RA = "SANDBOX-ADMIN"


def get_or_create_sandbox_student():
    """Aluno dedicado para a simulação do Admin — nunca gerado pelo seed_demo, nunca aparece
    junto das personas de demonstração. Criado uma única vez, sob demanda."""
    from apps.academic.models import Course
    from apps.students.models import Student

    User = get_user_model()

    user, _ = User.objects.get_or_create(
        username=SANDBOX_RA,
        defaults={"role": User.Role.STUDENT, "first_name": "Simulação", "last_name": "Admin"},
    )

    try:
        return user.student_profile
    except Student.DoesNotExist:
        pass

    course = Course.objects.filter(code="PED").first() or Course.objects.first()
    if course is None:
        raise RuntimeError("Nenhum curso cadastrado — rode seed_demo antes de usar a simulação.")
    return Student.objects.create(
        user=user, ra=SANDBOX_RA, course=course, current_period=course.internship_eligible_period,
    )
