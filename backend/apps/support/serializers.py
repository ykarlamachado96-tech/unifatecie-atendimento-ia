from rest_framework import serializers

from .models import Message, Ticket


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "ticket", "sender", "sender_type", "displayed_content", "moderation_status", "created_at")
        read_only_fields = fields


class TicketSerializer(serializers.ModelSerializer):
    student_ra = serializers.CharField(source="student.ra", read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id", "student", "student_ra", "student_name", "status", "intent",
            "assigned_monitor", "resolved_by", "created_at", "closed_at",
        )
        read_only_fields = ("status", "intent", "resolved_by", "created_at", "closed_at")

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username


class TicketDetailSerializer(TicketSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ("handoff_context", "messages")
