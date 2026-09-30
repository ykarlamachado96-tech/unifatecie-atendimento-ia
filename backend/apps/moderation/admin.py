from django.contrib import admin

from .models import Occurrence


@admin.register(Occurrence)
class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "category", "severity", "ticket", "detected_at")
    list_filter = ("category", "severity", "role")
    search_fields = ("user__username",)
    readonly_fields = ("original_message", "sanitized_message", "detected_at")
