from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdminUser
from apps.support.models import Ticket
from apps.support.serializers import MessageSerializer, TicketDetailSerializer, TicketSerializer

from .ingestion import ingest_source
from .harness import handle_incoming_message
from .models import AIProviderCredential, KnowledgeSource
from .sandbox import get_or_create_sandbox_student
from .serializers import AIProviderCredentialSerializer, KnowledgeSourceSerializer


class AIProviderCredentialListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        for value, _label in AIProviderCredential.Provider.choices:
            AIProviderCredential.objects.get_or_create(provider=value)
        qs = AIProviderCredential.objects.all().order_by("provider")
        return Response(AIProviderCredentialSerializer(qs, many=True).data)


class AIProviderCredentialDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        credential = get_object_or_404(AIProviderCredential, pk=pk)
        serializer = AIProviderCredentialSerializer(credential, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class KnowledgeSourceListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = KnowledgeSource.objects.all().order_by("-created_at")
        return Response(KnowledgeSourceSerializer(qs, many=True).data)

    def post(self, request):
        serializer = KnowledgeSourceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source = serializer.save()
        return Response(KnowledgeSourceSerializer(source).data, status=201)


class KnowledgeSourceProcessView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        source = get_object_or_404(KnowledgeSource, pk=pk)
        ingest_source(source)
        source.refresh_from_db()
        return Response(KnowledgeSourceSerializer(source).data)


class SandboxTicketListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        student = get_or_create_sandbox_student()
        qs = Ticket.objects.filter(student=student).order_by("-created_at")
        return Response(TicketSerializer(qs, many=True).data)

    def post(self, request):
        student = get_or_create_sandbox_student()
        ticket = Ticket.objects.create(student=student)
        return Response(TicketSerializer(ticket).data, status=201)


class SandboxTicketDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, ticket_id):
        student = get_or_create_sandbox_student()
        ticket = get_object_or_404(Ticket, pk=ticket_id, student=student)
        return Response(TicketDetailSerializer(ticket).data)


class SandboxMessageView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, ticket_id):
        student = get_or_create_sandbox_student()
        ticket = get_object_or_404(Ticket, pk=ticket_id, student=student)
        text = request.data.get("content", "").strip()
        if not text:
            return Response({"detail": "Mensagem vazia."}, status=400)
        message = handle_incoming_message(ticket=ticket, raw_text=text, sender_user=student.user)
        return Response(MessageSerializer(message).data, status=201)


class SandboxResetView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        student = get_or_create_sandbox_student()
        Ticket.objects.filter(student=student).delete()
        return Response(status=204)
