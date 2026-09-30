from django.contrib import admin

from .models import Evaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("ticket", "student", "monitor", "stars", "status", "deadline_at", "submitted_at")
    list_filter = ("status",)
    search_fields = ("student__ra",)
