from django.contrib import admin

from .models import InternshipFinalReport, InternshipRequirement, InternshipWaiver


@admin.register(InternshipRequirement)
class InternshipRequirementAdmin(admin.ModelAdmin):
    list_display = ("student", "stage", "status", "protocol_date", "decision_date")
    list_filter = ("stage", "status")
    search_fields = ("student__ra",)


@admin.register(InternshipWaiver)
class InternshipWaiverAdmin(admin.ModelAdmin):
    list_display = ("student", "kind", "status", "approved_percentage", "remaining_hours")
    list_filter = ("kind", "status")
    search_fields = ("student__ra", "protocol_number")


@admin.register(InternshipFinalReport)
class InternshipFinalReportAdmin(admin.ModelAdmin):
    list_display = ("student", "status", "submitted_at", "discipline_term_ends_at")
    list_filter = ("status",)
    search_fields = ("student__ra",)
