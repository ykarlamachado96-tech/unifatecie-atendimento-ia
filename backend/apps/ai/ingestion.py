import re

from django.utils import timezone

from .models import KnowledgeChunk, KnowledgeDocument, KnowledgeSource
from .providers import ProviderError, get_embedding_provider


def split_into_sections(markdown_text: str) -> list[str]:
    """Divide o markdown em blocos por cabeçalho de nível 1 ou 2 (# ou ## ...), mantendo o
    cabeçalho junto do seu conteúdo — cada bloco vira um KnowledgeChunk coerente. Documentos
    que misturam os dois níveis para os títulos de seção funcionam igual (### fica sempre
    dentro do bloco do pai)."""
    parts = re.split(r"\n(?=#{1,2} )", markdown_text)
    sections = [p.strip() for p in parts if p.strip()]
    return sections or ([markdown_text.strip()] if markdown_text.strip() else [])


def ingest_text(*, title: str, category: str, text: str, embed: bool = True) -> tuple[KnowledgeDocument, int, int]:
    """Cria/atualiza um KnowledgeDocument e seus KnowledgeChunk a partir de um texto bruto.
    Retorna (document, total_chunks, chunks_com_embedding)."""
    sections = split_into_sections(text)

    document, _ = KnowledgeDocument.objects.update_or_create(title=title, defaults={"category": category})
    document.chunks.all().delete()

    provider = get_embedding_provider() if embed else None
    embedded_count = 0
    chunks = []
    for section in sections:
        embedding = None
        if provider is not None:
            try:
                embedding = provider.embed(section)
                embedded_count += 1
            except ProviderError:
                pass
        chunks.append(KnowledgeChunk(document=document, content=section, embedding=embedding))

    KnowledgeChunk.objects.bulk_create(chunks)
    return document, len(chunks), embedded_count


def ingest_source(source: KnowledgeSource) -> KnowledgeSource:
    """Processa um KnowledgeSource (upload ou texto colado), gera o KnowledgeDocument
    correspondente e marca o resultado no próprio registro — usado pela action do Django Admin
    e reaproveitável por qualquer outro caminho (comando de terminal, por exemplo)."""
    try:
        if source.file:
            text = source.file.read().decode("utf-8")
        elif source.raw_text.strip():
            text = source.raw_text
        else:
            raise ValueError("Informe um arquivo ou cole o texto da fonte antes de processar.")

        document, _total, _embedded = ingest_text(title=source.title, category=source.category, text=text)

        source.document = document
        source.status = KnowledgeSource.Status.PROCESSED
        source.error_message = ""
    except Exception as exc:  # noqa: BLE001 - qualquer falha de processamento vira status de erro visível no Admin
        source.status = KnowledgeSource.Status.ERROR
        source.error_message = str(exc)[:500]
    finally:
        source.processed_at = timezone.now()
        source.save(update_fields=["document", "status", "error_message", "processed_at"])

    return source
