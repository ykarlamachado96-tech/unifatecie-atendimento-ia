from pgvector.django import L2Distance

from apps.ai.providers import ProviderError, get_embedding_provider


def search_knowledge_base(student, query=None, **kwargs):
    if not query:
        return {"results": []}

    from apps.ai.models import KnowledgeChunk

    try:
        provider = get_embedding_provider()
        query_embedding = provider.embed(query)
        qs = (
            KnowledgeChunk.objects.exclude(embedding__isnull=True)
            .select_related("document")
            .order_by(L2Distance("embedding", query_embedding))[:3]
        )
        results = [{"document": c.document.title, "content": c.content} for c in qs]
        if results:
            return {"results": results, "method": "embedding"}
    except ProviderError:
        pass

    qs = KnowledgeChunk.objects.filter(content__icontains=query).select_related("document")[:3]
    return {
        "results": [{"document": c.document.title, "content": c.content} for c in qs],
        "method": "keyword_fallback",
    }
