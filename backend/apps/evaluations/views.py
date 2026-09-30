from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Evaluation
from .serializers import EvaluationSerializer, SubmitEvaluationSerializer


class EvaluationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        evaluation = get_object_or_404(Evaluation, ticket_id=ticket_id)
        if request.user.role == "STUDENT" and evaluation.student.user_id != request.user.id:
            return Response({"detail": "Não autorizado."}, status=403)
        return Response(EvaluationSerializer(evaluation).data)

    def post(self, request, ticket_id):
        evaluation = get_object_or_404(
            Evaluation, ticket_id=ticket_id, status=Evaluation.Status.PENDING,
            student__user=request.user,
        )
        serializer = SubmitEvaluationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evaluation.stars = serializer.validated_data["stars"]
        evaluation.comment = serializer.validated_data["comment"]
        evaluation.status = Evaluation.Status.SUBMITTED
        evaluation.submitted_at = timezone.now()
        evaluation.save(update_fields=["stars", "comment", "status", "submitted_at"])
        return Response(EvaluationSerializer(evaluation).data)
