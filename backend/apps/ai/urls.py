from django.urls import path

from .views import (
    AIProviderCredentialDetailView,
    AIProviderCredentialListView,
    KnowledgeSourceListCreateView,
    KnowledgeSourceProcessView,
    SandboxMessageView,
    SandboxResetView,
    SandboxTicketDetailView,
    SandboxTicketListCreateView,
)

urlpatterns = [
    path("providers/", AIProviderCredentialListView.as_view(), name="ai-provider-list"),
    path("providers/<int:pk>/", AIProviderCredentialDetailView.as_view(), name="ai-provider-detail"),
    path("knowledge-sources/", KnowledgeSourceListCreateView.as_view(), name="knowledge-source-list-create"),
    path(
        "knowledge-sources/<int:pk>/process/",
        KnowledgeSourceProcessView.as_view(),
        name="knowledge-source-process",
    ),
    path("sandbox/tickets/", SandboxTicketListCreateView.as_view(), name="sandbox-ticket-list-create"),
    path("sandbox/tickets/<int:ticket_id>/", SandboxTicketDetailView.as_view(), name="sandbox-ticket-detail"),
    path(
        "sandbox/tickets/<int:ticket_id>/messages/",
        SandboxMessageView.as_view(),
        name="sandbox-ticket-messages",
    ),
    path("sandbox/reset/", SandboxResetView.as_view(), name="sandbox-reset"),
]
