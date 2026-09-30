from rest_framework import serializers

from .models import Evaluation


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = (
            "id", "ticket", "student", "monitor", "stars", "comment",
            "status", "created_at", "deadline_at", "submitted_at",
        )
        read_only_fields = ("id", "ticket", "student", "monitor", "status", "created_at", "deadline_at", "submitted_at")


class SubmitEvaluationSerializer(serializers.Serializer):
    stars = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
