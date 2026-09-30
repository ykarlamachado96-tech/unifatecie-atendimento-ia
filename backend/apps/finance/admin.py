from django.contrib import admin

from .models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "reference_month", "amount", "due_date", "status", "paid_at")
    list_filter = ("status",)
    search_fields = ("student__ra",)
