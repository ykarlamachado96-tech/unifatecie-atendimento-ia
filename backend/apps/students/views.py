from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsStudentUser
from apps.integrations.connectors import get_connector


class MyAcademicSummaryView(APIView):
    """Resumo acadêmico do aluno logado — reaproveita o mesmo AcademicConnector
    usado pelas ferramentas de IA, garantindo que aluno e IA vejam o mesmo dado."""

    permission_classes = [IsStudentUser]

    def get(self, request):
        student = request.user.student_profile
        connector = get_connector()

        enrollments = connector.get_student_enrollments(student.id)
        current_subjects = [e for e in enrollments if e["status"] == "IN_PROGRESS"]

        activities = connector.get_student_activities(student.id)
        pending_activities = [a for a in activities if a["status"] in ("PENDING", "LATE")]

        return Response({
            "ra": student.ra,
            "course": student.course.name,
            "current_period": student.current_period,
            "academic_status": student.academic_status,
            "current_subjects": current_subjects,
            "pending_activities": pending_activities,
            "financial_status": connector.get_student_financial_status(student.id),
            "open_invoices": connector.get_open_invoices(student.id),
            "internship_status": connector.get_student_internship_status(student.id),
        })
