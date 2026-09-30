from abc import ABC, abstractmethod
from decimal import Decimal


class AcademicConnector(ABC):
    """Interface de integração acadêmica (documento, seção 7).

    A aplicação nunca acessa diretamente as regras de um banco real: sempre
    passa por um connector. O MVP usa MockFateceConnector; quando houver
    acesso à base real da FATECE, basta trocar por RealFateceConnector.
    """

    @abstractmethod
    def get_student_profile(self, student_id: int) -> dict: ...

    @abstractmethod
    def get_student_course(self, student_id: int) -> dict: ...

    @abstractmethod
    def get_student_enrollments(self, student_id: int) -> list[dict]: ...

    @abstractmethod
    def get_student_subjects(self, student_id: int) -> list[dict]: ...

    @abstractmethod
    def get_subject_details(self, subject_code: str) -> dict: ...

    @abstractmethod
    def get_student_activities(self, student_id: int) -> list[dict]: ...

    @abstractmethod
    def get_activity_status(self, student_id: int, subject_code: str | None = None) -> list[dict]: ...

    @abstractmethod
    def get_student_financial_status(self, student_id: int) -> dict: ...

    @abstractmethod
    def get_open_invoices(self, student_id: int) -> list[dict]: ...

    @abstractmethod
    def get_invoice_details(self, student_id: int, invoice_id: int) -> dict: ...

    @abstractmethod
    def get_student_internship_status(self, student_id: int) -> dict: ...

    @abstractmethod
    def get_internship_requirements(self, student_id: int) -> dict: ...

    @abstractmethod
    def get_internship_documents(self, student_id: int) -> list[dict]: ...


class MockFateceConnector(AcademicConnector):
    """Implementação sobre a base simulada (modelos Django locais)."""

    def get_student_profile(self, student_id):
        from apps.students.models import Student

        student = Student.objects.select_related("user", "course").get(pk=student_id)
        return {
            "student_id": student.id,
            "ra": student.ra,
            "name": student.user.get_full_name() or student.user.username,
            "course": student.course.name,
            "current_period": student.current_period,
            "academic_status": student.academic_status,
            "behavior_score": student.user.behavior_score,
        }

    def get_student_course(self, student_id):
        from apps.students.models import Student

        student = Student.objects.select_related("course").get(pk=student_id)
        return {
            "course_code": student.course.code,
            "course_name": student.course.name,
            "total_periods": student.course.total_periods,
            "current_period": student.current_period,
        }

    def get_student_enrollments(self, student_id):
        from apps.students.models import Enrollment

        qs = Enrollment.objects.filter(student_id=student_id).select_related("subject")
        return [
            {
                "subject_code": e.subject.code,
                "subject_name": e.subject.name,
                "period": e.period,
                "status": e.status,
                "grade": float(e.grade) if e.grade is not None else None,
            }
            for e in qs
        ]

    def get_student_subjects(self, student_id):
        return [
            e for e in self.get_student_enrollments(student_id)
            if e["status"] == "IN_PROGRESS"
        ]

    def get_subject_details(self, subject_code):
        from apps.academic.models import Subject

        subject = Subject.objects.select_related("course").get(code=subject_code)
        return {
            "subject_code": subject.code,
            "subject_name": subject.name,
            "course": subject.course.name,
            "period": subject.period,
            "workload": subject.workload,
        }

    def get_student_activities(self, student_id):
        from apps.students.models import Activity

        qs = Activity.objects.filter(student_id=student_id).select_related("subject")
        return [
            {
                "subject_code": a.subject.code,
                "title": a.title,
                "due_date": a.due_date.isoformat(),
                "status": a.status,
            }
            for a in qs
        ]

    def get_activity_status(self, student_id, subject_code=None):
        activities = self.get_student_activities(student_id)
        if subject_code:
            activities = [a for a in activities if a["subject_code"] == subject_code]
        return activities

    def get_student_financial_status(self, student_id):
        from apps.finance.models import FinancialRecord

        qs = FinancialRecord.objects.filter(student_id=student_id).order_by("-reference_month")
        total_overdue = sum(
            (r.amount for r in qs if r.status == FinancialRecord.Status.OVERDUE), Decimal("0")
        )
        return {
            "has_overdue": qs.filter(status=FinancialRecord.Status.OVERDUE).exists(),
            "total_overdue": float(total_overdue),
            "records_count": qs.count(),
        }

    def get_open_invoices(self, student_id):
        from apps.finance.models import FinancialRecord

        qs = FinancialRecord.objects.filter(
            student_id=student_id,
            status__in=[FinancialRecord.Status.PENDING, FinancialRecord.Status.OVERDUE],
        ).order_by("due_date")
        return [
            {
                "invoice_id": r.id,
                "reference_month": r.reference_month.isoformat(),
                "amount": float(r.amount),
                "due_date": r.due_date.isoformat(),
                "status": r.status,
            }
            for r in qs
        ]

    def get_invoice_details(self, student_id, invoice_id):
        from apps.finance.models import FinancialRecord

        record = FinancialRecord.objects.get(pk=invoice_id, student_id=student_id)
        return {
            "invoice_id": record.id,
            "reference_month": record.reference_month.isoformat(),
            "amount": float(record.amount),
            "due_date": record.due_date.isoformat(),
            "status": record.status,
            "paid_at": record.paid_at.isoformat() if record.paid_at else None,
            "barcode": record.barcode,
        }

    def _internship_overview(self, student_id):
        from apps.internship.models import (
            STAGE_HOURS,
            STAGE_ORDER,
            TOTAL_INTERNSHIP_HOURS,
            InternshipFinalReport,
            InternshipRequirement,
            InternshipStage,
            InternshipWaiver,
        )
        from apps.students.models import Student

        student = Student.objects.select_related("course").get(pk=student_id)
        eligible_period = student.course.internship_eligible_period
        is_eligible = student.current_period >= eligible_period

        requirements_by_stage = {
            r.stage: r for r in InternshipRequirement.objects.filter(student_id=student_id)
        }
        stages = []
        for stage in STAGE_ORDER:
            req = requirements_by_stage.get(stage)
            stages.append({
                "stage": stage,
                "stage_label": InternshipStage(stage).label,
                "required_hours": STAGE_HOURS[stage],
                "status": req.status if req else InternshipRequirement.Status.NOT_REQUESTED,
                "host_institution": req.host_institution if req else "",
                "protocol_date": req.protocol_date.isoformat() if req and req.protocol_date else None,
                "decision_date": req.decision_date.isoformat() if req and req.decision_date else None,
                "planned_start_date": (
                    req.planned_start_date.isoformat() if req and req.planned_start_date else None
                ),
                "rejection_reason": req.rejection_reason if req else "",
            })

        waiver = (
            InternshipWaiver.objects.filter(student_id=student_id, status=InternshipWaiver.Status.APPROVED)
            .order_by("-id").first()
        )
        final_report, _ = InternshipFinalReport.objects.get_or_create(student_id=student_id)

        active_requirement_in_analysis = any(
            s["status"] == InternshipRequirement.Status.IN_ANALYSIS for s in stages
        )
        next_requestable_stage = None
        if is_eligible and not active_requirement_in_analysis:
            for s in stages:
                if s["status"] in (InternshipRequirement.Status.NOT_REQUESTED, InternshipRequirement.Status.REJECTED):
                    next_requestable_stage = s["stage"]
                    break

        if not is_eligible:
            overall = "NOT_ELIGIBLE"
        elif final_report.status == InternshipFinalReport.Status.APPROVED:
            overall = "COMPLETED"
        elif final_report.status == InternshipFinalReport.Status.DEPENDENCY:
            overall = "DEPENDENCY"
        elif final_report.status == InternshipFinalReport.Status.RETURNED_FOR_CORRECTION:
            overall = "PENDING_CORRECTION"
        elif final_report.status == InternshipFinalReport.Status.SUBMITTED:
            overall = "AWAITING_FINAL_REPORT_REVIEW"
        elif active_requirement_in_analysis:
            overall = "AWAITING_ANALYSIS"
        elif any(s["status"] == InternshipRequirement.Status.FORMALIZED for s in stages):
            overall = "IN_PROGRESS"
        elif all(s["status"] == InternshipRequirement.Status.COMPLETED for s in stages):
            overall = "AWAITING_FINAL_REPORT_REVIEW"
        else:
            overall = "NOT_STARTED"

        return {
            "status": overall,
            "overall_status": overall,
            "is_eligible": is_eligible,
            "eligible_from_period": eligible_period,
            "current_period": student.current_period,
            "stages": stages,
            "total_hours_required": TOTAL_INTERNSHIP_HOURS,
            "next_requestable_stage": next_requestable_stage,
            "has_active_requirement_in_analysis": active_requirement_in_analysis,
            "active_waiver": (
                {
                    "kind": waiver.kind,
                    "protocol_number": waiver.protocol_number,
                    "approved_percentage": waiver.approved_percentage,
                    "remaining_hours": waiver.remaining_hours,
                    "notes": waiver.notes,
                }
                if waiver else None
            ),
            "final_report": {
                "status": final_report.status,
                "submitted_at": final_report.submitted_at.isoformat() if final_report.submitted_at else None,
                "discipline_term_ends_at": (
                    final_report.discipline_term_ends_at.isoformat()
                    if final_report.discipline_term_ends_at else None
                ),
                "feedback": final_report.feedback,
            },
        }

    def get_student_internship_status(self, student_id):
        return self._internship_overview(student_id)

    def get_internship_requirements(self, student_id):
        from apps.internship.models import (
            MAX_DAILY_HOURS,
            MAX_WEEKLY_HOURS,
            MIN_START_ANTECEDENCE_BUSINESS_DAYS,
            TCE_ANALYSIS_DEADLINE_BUSINESS_DAYS,
        )

        overview = self._internship_overview(student_id)
        return {
            "is_eligible": overview["is_eligible"],
            "eligible_from_period": overview["eligible_from_period"],
            "current_period": overview["current_period"],
            "total_hours_required": overview["total_hours_required"],
            "one_requirement_in_analysis_at_a_time": True,
            "max_daily_hours": MAX_DAILY_HOURS,
            "max_weekly_hours": MAX_WEEKLY_HOURS,
            "tce_analysis_deadline_business_days": TCE_ANALYSIS_DEADLINE_BUSINESS_DAYS,
            "min_start_antecedence_business_days": MIN_START_ANTECEDENCE_BUSINESS_DAYS,
            "stages": overview["stages"],
            "next_requestable_stage": overview["next_requestable_stage"],
            "active_waiver": overview["active_waiver"],
        }

    def get_internship_documents(self, student_id):
        from apps.internship.models import FINAL_REPORT_CORRECTION_DEADLINE_BUSINESS_DAYS

        overview = self._internship_overview(student_id)
        return {
            "checklist": [
                {
                    "item": "Relatórios de Observação e Participação",
                    "quantity": 5,
                    "note": "1 por área: Educação Infantil, Língua Portuguesa, Matemática, Ciências, História/Geografia — não é 1 por dia.",
                },
                {
                    "item": "Relatórios de Regência",
                    "quantity": 5,
                    "note": "mesmas 5 áreas da Observação; Gestão Escolar não possui Relatório de Regência.",
                },
                {
                    "item": "Planos de Aula",
                    "quantity": 5,
                    "note": "mesmas 5 áreas; não é 1 plano por hora de Regência. Gestão não tem Plano de Aula.",
                },
                {
                    "item": "Formulários de Avaliação da Regência",
                    "quantity": 5,
                    "note": "preenchidos pelo professor regente/supervisor que acompanhou a Regência.",
                },
                {
                    "item": "Relatório de Gestão Escolar",
                    "quantity": 1,
                    "note": "com base na observação, participação e entrevista com a equipe gestora.",
                },
                {
                    "item": "Ficha(s) de Frequência",
                    "quantity": None,
                    "note": "uma por instituição/etapa, refletindo corretamente local, data e horário de cada atividade.",
                },
                {
                    "item": "Ficha de Autoavaliação",
                    "quantity": 1,
                    "note": "única para todo o estágio, mesmo com mais de uma escola.",
                },
                {
                    "item": "Relatório Final",
                    "quantity": 1,
                    "note": "único, reunindo todos os anexos digitalizados em um único arquivo PDF, sem links.",
                },
            ],
            "final_report": overview["final_report"],
            "final_report_correction_deadline_business_days": FINAL_REPORT_CORRECTION_DEADLINE_BUSINESS_DAYS,
        }


_connector_instance: AcademicConnector | None = None


def get_connector() -> AcademicConnector:
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = MockFateceConnector()
    return _connector_instance
