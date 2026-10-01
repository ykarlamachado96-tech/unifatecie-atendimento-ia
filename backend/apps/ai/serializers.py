from rest_framework import serializers

from .models import AIProviderCredential, KnowledgeSource


class AIProviderCredentialSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    api_key_display = serializers.SerializerMethodField()

    class Meta:
        model = AIProviderCredential
        fields = (
            "id", "provider", "api_key", "api_key_display", "base_url", "model_name",
            "is_active", "use_for_embeddings", "temperature", "max_tokens", "updated_at",
        )
        read_only_fields = ("id", "provider", "updated_at")

    def get_api_key_display(self, obj):
        return f"•••• {obj.api_key[-4:]}" if obj.api_key else ""

    def update(self, instance, validated_data):
        new_key = validated_data.pop("api_key", None)
        if new_key:
            instance.api_key = new_key
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class KnowledgeSourceSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True, default=None)

    class Meta:
        model = KnowledgeSource
        fields = (
            "id", "title", "category", "file", "raw_text", "document", "document_title",
            "status", "error_message", "processed_at", "created_at",
        )
        read_only_fields = ("document", "document_title", "status", "error_message", "processed_at", "created_at")
