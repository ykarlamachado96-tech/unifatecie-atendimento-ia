from django.contrib import admin

from .models import AIExecution, ConversationScore, KnowledgeChunk, KnowledgeDocument


@admin.register(AIExecution)
class AIExecutionAdmin(admin.ModelAdmin):
    list_display = ("ticket", "intent", "confidence", "tool", "latency_ms", "created_at")
    list_filter = ("provider", "tool")
    readonly_fields = ("input", "output")


@admin.register(ConversationScore)
class ConversationScoreAdmin(admin.ModelAdmin):
    list_display = ("ticket", "overall_score", "cooperation", "clarity", "respectfulness", "warnings")


class KnowledgeChunkInline(admin.TabularInline):
    model = KnowledgeChunk
    extra = 1
    exclude = ("embedding",)


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    list_filter = ("category",)
    inlines = [KnowledgeChunkInline]
