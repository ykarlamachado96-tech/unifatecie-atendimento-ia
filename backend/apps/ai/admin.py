from django import forms
from django.contrib import admin

from .ingestion import ingest_source
from .models import (
    AIExecution,
    AIProviderCredential,
    ConversationScore,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeSource,
)


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


class AIProviderCredentialForm(forms.ModelForm):
    api_key = forms.CharField(
        required=False, widget=forms.PasswordInput(render_value=False),
        help_text="Deixe em branco para manter a chave já salva.",
    )

    class Meta:
        model = AIProviderCredential
        fields = "__all__"

    def clean_api_key(self):
        value = self.cleaned_data["api_key"]
        if not value and self.instance.pk:
            return self.instance.api_key
        return value


@admin.register(AIProviderCredential)
class AIProviderCredentialAdmin(admin.ModelAdmin):
    form = AIProviderCredentialForm
    list_display = ("provider", "masked_api_key", "model_name", "is_active", "use_for_embeddings", "updated_at")
    list_editable = ("is_active", "use_for_embeddings")

    @admin.display(description="Chave de API")
    def masked_api_key(self, obj):
        if not obj.api_key:
            return "—"
        return f"•••• {obj.api_key[-4:]}"


@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "document", "processed_at")
    list_filter = ("category", "status")
    readonly_fields = ("document", "status", "error_message", "processed_at")
    actions = ["processar_fonte"]

    @admin.action(description="Processar e carregar na base de conhecimento")
    def processar_fonte(self, request, queryset):
        processed, errors = 0, 0
        for source in queryset:
            ingest_source(source)
            source.refresh_from_db()
            if source.status == KnowledgeSource.Status.PROCESSED:
                processed += 1
            else:
                errors += 1
        if processed:
            self.message_user(request, f"{processed} fonte(s) processada(s) com sucesso.")
        if errors:
            self.message_user(request, f"{errors} fonte(s) com erro — veja a coluna de status.", level="ERROR")
