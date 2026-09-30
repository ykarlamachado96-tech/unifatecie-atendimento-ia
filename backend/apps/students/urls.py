from django.urls import path

from .views import MyAcademicSummaryView

urlpatterns = [
    path("me/summary/", MyAcademicSummaryView.as_view(), name="student-summary"),
]
