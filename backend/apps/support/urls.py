from django.urls import path

from .views import (
    AssignTicketView,
    CloseTicketView,
    MessageListCreateView,
    QueueView,
    TicketDetailView,
    TicketListCreateView,
    TransferTicketView,
)

urlpatterns = [
    path("tickets/", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("tickets/queue/", QueueView.as_view(), name="ticket-queue"),
    path("tickets/<int:ticket_id>/", TicketDetailView.as_view(), name="ticket-detail"),
    path("tickets/<int:ticket_id>/messages/", MessageListCreateView.as_view(), name="ticket-messages"),
    path("tickets/<int:ticket_id>/assign/", AssignTicketView.as_view(), name="ticket-assign"),
    path("tickets/<int:ticket_id>/transfer/", TransferTicketView.as_view(), name="ticket-transfer"),
    path("tickets/<int:ticket_id>/close/", CloseTicketView.as_view(), name="ticket-close"),
]
