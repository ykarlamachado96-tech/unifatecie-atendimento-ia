import re

from django.core.management.base import BaseCommand

from apps.ai.models import KnowledgeChunk, KnowledgeDocument
from apps.ai.providers import ProviderError, get_provider

SOURCES = [
    {
        "title": "Diretrizes de Estágio Obrigatório — Pedagogia",
        "category": KnowledgeDocument.Category.INTERNSHIP_RULES,
        "path": "apps/ai/knowledge_sources/diretrizes_estagio_pedagogia.md",
    },
]


def _split_into_sections(markdown_text: str) -> list[str]:
    """Divide o markdown em blocos por cabeçalho de nível 1 ou 2 (# ou ## ...),
    mantendo o cabeçalho junto do seu conteúdo — cada bloco vira um KnowledgeChunk
    coerente. O documento-fonte mistura os dois níveis para os títulos de seção
    (### fica sempre dentro do bloco do pai)."""
    parts = re.split(r"\n(?=#{1,2} )", markdown_text)
    sections = [p.strip() for p in parts if p.strip()]
    return sections


class Command(BaseCommand):
    help = "Carrega os documentos de conhecimento (diretrizes de estágio, etc.) para o RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-embed", action="store_true",
            help="Não gera embeddings (só popula os chunks; a busca cai para o fallback por palavra-chave).",
        )

    def handle(self, *args, **options):
        from pathlib import Path

        from django.conf import settings

        provider = get_provider() if not options["no_embed"] else None

        for source in SOURCES:
            file_path = Path(settings.BASE_DIR) / source["path"]
            if not file_path.exists():
                self.stdout.write(self.style.ERROR(f"Arquivo não encontrado: {file_path}"))
                continue

            text = file_path.read_text(encoding="utf-8")
            sections = _split_into_sections(text)

            document, _ = KnowledgeDocument.objects.update_or_create(
                title=source["title"], defaults={"category": source["category"]},
            )
            document.chunks.all().delete()

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
            self.stdout.write(self.style.SUCCESS(
                f"'{document.title}': {len(chunks)} chunks criados "
                f"({embedded_count} com embedding, {len(chunks) - embedded_count} via fallback por palavra-chave)."
            ))
