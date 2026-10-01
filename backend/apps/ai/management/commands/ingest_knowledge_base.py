from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.ai.ingestion import ingest_text
from apps.ai.models import KnowledgeDocument

SOURCES = [
    {
        "title": "Diretrizes de Estágio Obrigatório — Pedagogia",
        "category": KnowledgeDocument.Category.INTERNSHIP_RULES,
        "path": "apps/ai/knowledge_sources/diretrizes_estagio_pedagogia.md",
    },
]


class Command(BaseCommand):
    help = "Carrega os documentos de conhecimento (diretrizes de estágio, etc.) para o RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-embed", action="store_true",
            help="Não gera embeddings (só popula os chunks; a busca cai para o fallback por palavra-chave).",
        )

    def handle(self, *args, **options):
        for source in SOURCES:
            file_path = Path(settings.BASE_DIR) / source["path"]
            if not file_path.exists():
                self.stdout.write(self.style.ERROR(f"Arquivo não encontrado: {file_path}"))
                continue

            text = file_path.read_text(encoding="utf-8")
            document, total, embedded = ingest_text(
                title=source["title"], category=source["category"], text=text, embed=not options["no_embed"],
            )
            self.stdout.write(self.style.SUCCESS(
                f"'{document.title}': {total} chunks criados "
                f"({embedded} com embedding, {total - embedded} via fallback por palavra-chave)."
            ))
