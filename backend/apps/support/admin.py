from django.contrib import admin

from .models import Message, Ticket


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender_type", "original_content", "displayed_content", "moderation_status", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "status", "intent", "assigned_monitor", "resolved_by", "created_at", "closed_at")
    list_filter = ("status", "resolved_by")
    search_fields = ("student__ra",)
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "sender_type", "moderation_status", "created_at")
    list_filter = ("sender_type", "moderation_status")
