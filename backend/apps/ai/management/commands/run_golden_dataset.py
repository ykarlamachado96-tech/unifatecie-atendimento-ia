from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.ai.golden_dataset import GOLDEN_CASES
from apps.ai.harness import handle_incoming_message
from apps.students.models import Student
from apps.support.models import Ticket

User = get_user_model()


class Command(BaseCommand):
    help = "Executa o Golden Dataset (documento, seções 27-28) e reporta métricas de assertividade."

    def handle(self, *args, **options):
        results = [
            self._run_ai_case(case) if case["type"] == "ai_intent" else self._run_moderation_case(case)
            for case in GOLDEN_CASES
        ]
        self._print_report(results)

    def _run_ai_case(self, case):
        student = Student.objects.select_related("user").get(user__username=case["student_username"])
        ticket = Ticket.objects.create(student=student)
        handle_incoming_message(ticket=ticket, raw_text=case["question"], sender_user=student.user)
        ticket.refresh_from_db()
        execution = ticket.ai_executions.order_by("-created_at").first()

        actual_tool = execution.tool or None if execution else None
        tool_ok = actual_tool == case["expected_tool"]
        actual_requires_human = ticket.status == Ticket.Status.WAITING_HUMAN
        handoff_ok = actual_requires_human == case["expected_requires_human"]

        return {
            "id": case["id"], "type": "ai_intent", "tool_ok": tool_ok, "handoff_ok": handoff_ok,
            "detail": (
                f"tool_esperada={case['expected_tool']} tool_obtida={actual_tool} "
                f"status={ticket.status} erro_ia={execution.error if execution else None}"
            ),
        }

    def _run_moderation_case(self, case):
        student = Student.objects.select_related("user").get(user__username=case["student_username"])
        ticket = Ticket.objects.create(student=student)
        sender = (
            User.objects.filter(role="MONITOR").first()
            if case["sender_role"] == "MONITOR"
            else student.user
        )
        handle_incoming_message(ticket=ticket, raw_text=case["message"], sender_user=sender)
        flagged = ticket.occurrences.exists()

        return {
            "id": case["id"], "type": "moderation",
            "moderation_ok": flagged == case["expected_flagged"],
            "detail": f"flagged_esperado={case['expected_flagged']} flagged_obtido={flagged}",
        }

    def _print_report(self, results):
        ai_cases = [r for r in results if r["type"] == "ai_intent"]
        mod_cases = [r for r in results if r["type"] == "moderation"]

        self.stdout.write("\n=== Golden Dataset — Relatório ===\n")
        for r in results:
            status = "OK" if r.get("tool_ok", r.get("moderation_ok")) or r.get("handoff_ok", True) else "FALHOU"
            self.stdout.write(f"[{status}] {r['id']}: {r['detail']}")

        def pct(n, total):
            return f"{(n / total * 100):.0f}%" if total else "n/a"

        tool_hits = sum(1 for r in ai_cases if r["tool_ok"])
        handoff_hits = sum(1 for r in ai_cases if r["handoff_ok"])
        mod_hits = sum(1 for r in mod_cases if r["moderation_ok"])

        self.stdout.write("\n--- Métricas (documento, seção 28) ---")
        self.stdout.write(f"Tool Selection Accuracy: {pct(tool_hits, len(ai_cases))} ({tool_hits}/{len(ai_cases)})")
        self.stdout.write(f"Handoff Accuracy: {pct(handoff_hits, len(ai_cases))} ({handoff_hits}/{len(ai_cases)})")
        self.stdout.write(f"Moderation Accuracy: {pct(mod_hits, len(mod_cases))} ({mod_hits}/{len(mod_cases)})")

        from apps.ai.providers import get_provider
        provider = get_provider()
        note = "modelos locais menores tendem a responder sem acionar ferramentas." if provider.name == "local" else (
            "divergências de Tool Selection podem ser ferramentas semanticamente equivalentes "
            "(ex.: get_student_internship_status vs. get_internship_requirements) — revise o "
            "golden_dataset.py se o \"esperado\" estiver desatualizado, não assuma que é erro do modelo."
        )
        self.stdout.write(self.style.WARNING(
            f"\nObs: execução com provider='{provider.name}' modelo='{provider.model_name}'. {note}"
        ))
