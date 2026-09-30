from django.urls import path

from .views import EvaluationDetailView

urlpatterns = [
    path("<int:ticket_id>/", EvaluationDetailView.as_view(), name="evaluation-detail"),
]
