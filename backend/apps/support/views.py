from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.harness import handle_incoming_message
from apps.ai.scoring import score_ticket_conversation
from apps.common.permissions import IsMonitorUser
from apps.evaluations.services import create_pending_evaluation

from .models import Message, Ticket
from .serializers import MessageSerializer, TicketDetailSerializer, TicketSerializer


def _ticket_queryset_for(user):
    if user.role == "STUDENT":
        return Ticket.objects.filter(student__user=user)
    if user.role == "MONITOR":
        return Ticket.objects.filter(assigned_monitor=user) | Ticket.objects.filter(
            status=Ticket.Status.WAITING_HUMAN
        )
    return Ticket.objects.all()


class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = _ticket_queryset_for(request.user).distinct().select_related("student__user")
        return Response(TicketSerializer(tickets, many=True).data)

    def post(self, request):
        if request.user.role != "STUDENT":
            return Response({"detail": "Apenas alunos podem iniciar um atendimento."}, status=403)
        ticket = Ticket.objects.create(student=request.user.student_profile)
        return Response(TicketSerializer(ticket).data, status=201)


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(_ticket_queryset_for(request.user), pk=ticket_id)
        return Response(TicketDetailSerializer(ticket).data)


class QueueView(APIView):
    permission_classes = [IsMonitorUser]

    def get(self, request):
        tickets = Ticket.objects.filter(status=Ticket.Status.WAITING_HUMAN).select_related("student__user")
        return Response(TicketSerializer(tickets, many=True).data)


class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(_ticket_queryset_for(request.user), pk=ticket_id)
        since = request.query_params.get("since")
        qs = ticket.messages.all()
        if since:
            qs = qs.filter(created_at__gt=since)
        return Response(MessageSerializer(qs, many=True).data)

    def post(self, request, ticket_id):
        ticket = get_object_or_404(_ticket_queryset_for(request.user), pk=ticket_id)
        text = request.data.get("content", "").strip()
        if not text:
            return Response({"detail": "Mensagem vazia."}, status=400)
        message = handle_incoming_message(ticket=ticket, raw_text=text, sender_user=request.user)
        return Response(MessageSerializer(message).data, status=201)


class AssignTicketView(APIView):
    permission_classes = [IsMonitorUser]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id, status=Ticket.Status.WAITING_HUMAN)
        ticket.assigned_monitor = request.user
        ticket.status = Ticket.Status.HUMAN_ASSIGNED
        ticket.save(update_fields=["assigned_monitor", "status"])
        return Response(TicketDetailSerializer(ticket).data)


class TransferTicketView(APIView):
    permission_classes = [IsMonitorUser]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id, assigned_monitor=request.user)
        ticket.assigned_monitor = None
        ticket.status = Ticket.Status.WAITING_HUMAN
        ticket.save(update_fields=["assigned_monitor", "status"])
        return Response(TicketSerializer(ticket).data)


class CloseTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        user = request.user
        if user.role == "MONITOR":
            ticket = get_object_or_404(Ticket, pk=ticket_id, assigned_monitor=user)
            resolved_by = Ticket.ResolvedBy.HUMAN
        elif user.role == "STUDENT":
            ticket = get_object_or_404(
                Ticket, pk=ticket_id, student__user=user,
                status__in=[Ticket.Status.AI_WAITING_USER, Ticket.Status.RESOLVED],
            )
            resolved_by = Ticket.ResolvedBy.AI
        else:
            return Response({"detail": "Papel não autorizado a encerrar atendimentos."}, status=403)

        ticket.status = Ticket.Status.CLOSED
        ticket.resolved_by = resolved_by
        ticket.closed_at = timezone.now()
        ticket.save(update_fields=["status", "resolved_by", "closed_at"])
        score_ticket_conversation(ticket)
        create_pending_evaluation(ticket)
        return Response(TicketSerializer(ticket).data)
