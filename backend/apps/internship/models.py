from django.db import models


class InternshipStage(models.TextChoices):
    """As três etapas do Estágio Supervisionado Obrigatório em Pedagogia
    (diretrizes, seção 5.2). Cada etapa tem seu próprio Termo de Compromisso
    (seção 9.2) — nunca um processo único para as três."""

    EDUCACAO_INFANTIL = "EDUCACAO_INFANTIL", "Educação Infantil"
    ENSINO_FUNDAMENTAL_ANOS_INICIAIS = "ENSINO_FUNDAMENTAL_ANOS_INICIAIS", "Ensino Fundamental — Anos Iniciais"
    GESTAO_ESCOLAR = "GESTAO_ESCOLAR", "Gestão Escolar"


STAGE_ORDER = [
    InternshipStage.EDUCACAO_INFANTIL,
    InternshipStage.ENSINO_FUNDAMENTAL_ANOS_INICIAIS,
    InternshipStage.GESTAO_ESCOLAR,
]

# Carga horária presencial por etapa (diretrizes, seção 5.2) — fonte única da
# verdade, nunca recalculada por fórmula genérica (seção 52).
STAGE_HOURS = {
    InternshipStage.EDUCACAO_INFANTIL: 16,
    InternshipStage.ENSINO_FUNDAMENTAL_ANOS_INICIAIS: 64,
    InternshipStage.GESTAO_ESCOLAR: 16,
}
TOTAL_INTERNSHIP_HOURS = sum(STAGE_HOURS.values())  # 96h (seção 5.1)

MAX_DAILY_HOURS = 6  # seção 6
MAX_WEEKLY_HOURS = 30  # seção 6
TCE_ANALYSIS_DEADLINE_BUSINESS_DAYS = 7  # seção 9.4
MIN_START_ANTECEDENCE_BUSINESS_DAYS = 7  # seção 9.5
FINAL_REPORT_CORRECTION_DEADLINE_BUSINESS_DAYS = 7  # seção 32.1 — contado do encerramento da vigência, não do envio


class InternshipRequirement(models.Model):
    """Um Termo de Compromisso/requerimento por etapa (seção 9.2). O sistema só
    permite um requerimento em andamento por vez por aluno (seção 9.3) — a
    etapa seguinte só é solicitada após a finalização (deferimento ou
    indeferimento) da etapa anterior, não sua conclusão presencial."""

    class Status(models.TextChoices):
        NOT_REQUESTED = "NOT_REQUESTED", "Não solicitado"
        IN_ANALYSIS = "IN_ANALYSIS", "Em análise"
        FORMALIZED = "FORMALIZED", "Formalizado"
        REJECTED = "REJECTED", "Indeferido"
        COMPLETED = "COMPLETED", "Concluído"

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="internship_requirements"
    )
    stage = models.CharField(max_length=40, choices=InternshipStage.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_REQUESTED)
    host_institution = models.CharField(max_length=200, blank=True)
    protocol_date = models.DateField(null=True, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    planned_start_date = models.DateField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "stage"], name="unique_requirement_per_stage")
        ]
        ordering = ["student_id", "stage"]

    def __str__(self):
        return f"{self.student} - {self.get_stage_display()} ({self.status})"


class InternshipWaiver(models.Model):
    """Dispensa parcial por atividades profissionais (seção 28) ou convalidação
    de estágio não obrigatório/remunerado (seção 29). O percentual e as horas
    restantes vêm sempre do parecer/protocolo individual já deferido — nunca
    recalculados por fórmula genérica (seções 30, 31, 52)."""

    class Kind(models.TextChoices):
        PROFESSIONAL_ACTIVITY = "PROFESSIONAL_ACTIVITY", "Dispensa por atividades profissionais"
        NON_MANDATORY_CONVALIDATION = "NON_MANDATORY_CONVALIDATION", "Convalidação de estágio não obrigatório"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Em análise"
        APPROVED = "APPROVED", "Deferido"
        REJECTED = "REJECTED", "Indeferido"

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="internship_waivers"
    )
    kind = models.CharField(max_length=30, choices=Kind.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    protocol_number = models.CharField(max_length=30, blank=True)
    approved_percentage = models.PositiveSmallIntegerField(null=True, blank=True)
    remaining_hours = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.student} - {self.get_kind_display()} ({self.status})"


class InternshipFinalReport(models.Model):
    """Relatório Final do estágio — sempre um único trabalho (seção 25), mesmo
    com múltiplas etapas/escolas. O prazo de correção conta a partir do
    encerramento da vigência da disciplina, não da data de envio (seção 32.1)."""

    class Status(models.TextChoices):
        NOT_SUBMITTED = "NOT_SUBMITTED", "Não enviado"
        SUBMITTED = "SUBMITTED", "Enviado, aguardando correção"
        RETURNED_FOR_CORRECTION = "RETURNED_FOR_CORRECTION", "Devolvido para correção"
        APPROVED = "APPROVED", "Aprovado"
        DEPENDENCY = "DEPENDENCY", "Disciplina encerrada sem conclusão (Regime de Dependência)"

    student = models.OneToOneField(
        "students.Student", on_delete=models.CASCADE, related_name="internship_final_report"
    )
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NOT_SUBMITTED)
    submitted_at = models.DateField(null=True, blank=True)
    discipline_term_ends_at = models.DateField(null=True, blank=True)
    feedback = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.student} - Relatório Final ({self.status})"
