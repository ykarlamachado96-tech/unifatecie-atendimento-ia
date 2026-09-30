import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.academic.models import Course, Subject
from apps.ai.models import AIExecution, ConversationScore
from apps.evaluations.models import Evaluation
from apps.finance.models import FinancialRecord
from apps.internship.models import (
    STAGE_ORDER,
    InternshipFinalReport,
    InternshipRequirement,
    InternshipWaiver,
)
from apps.moderation.models import Occurrence
from apps.students.models import Activity, Enrollment, Student
from apps.support.models import Message, Ticket

User = get_user_model()
fake = Faker("pt_BR")

STAFF_PASSWORD = "demo123"

COURSES = [
    ("Análise e Desenvolvimento de Sistemas", "ADS", 6),
    ("Ciência da Computação", "CC", 8),
    ("Redes de Computadores", "REDES", 6),
    ("Segurança da Informação", "SEGINFO", 6),
    ("Administração", "ADM", 8),
    ("Gestão Comercial", "GCOM", 4),
    ("Recursos Humanos", "RH", 4),
    ("Marketing", "MKT", 4),
    ("Logística", "LOG", 4),
    ("Engenharia de Produção", "ENGP", 10),
    ("Contabilidade", "CONT", 8),
    ("Design Gráfico", "DESIGN", 4),
    ("Pedagogia", "PED", 8),
    ("Enfermagem", "ENF", 10),
    ("Direito", "DIR", 10),
]

TOPICS = [
    "Cálculo", "Programação", "Banco de Dados", "Redes de Computadores", "Estatística",
    "Direito Civil", "Contabilidade Geral", "Marketing Digital", "Gestão de Pessoas",
    "Empreendedorismo", "Ética Profissional", "Metodologia Científica", "Algoritmos",
    "Estrutura de Dados", "Engenharia de Software", "Sistemas Operacionais",
    "Segurança da Informação", "Inteligência Artificial", "Economia",
    "Administração Financeira", "Logística Empresarial", "Qualidade e Produtividade",
    "Anatomia", "Fisiologia", "Psicologia Educacional", "Didática",
    "Design de Interfaces", "Modelagem de Dados", "Cloud Computing",
    "Legislação Trabalhista", "Comunicação Empresarial", "Matemática Financeira",
]

# Arquétipos de aluno (documento, seção 4). Cada um combina, de forma coerente,
# progressão de matrícula (períodos encerrados x período vigente, ao estilo
# Moodle), situação financeira e situação de estágio — em vez de sortear cada
# dimensão isoladamente e gerar combinações sem sentido.
ARCHETYPES = [
    ("veterano_ok", 38),          # progride normal, matérias fechadas aprovadas, vigentes em andamento
    ("com_dependencia", 20),      # reprovou uma matéria e está refazendo (dependência) junto das vigentes
    ("calouro", 10),               # primeiro período, sem histórico
    ("trancamento", 5),            # trancado: tem histórico, mas nenhuma matéria vigente agora
    ("matricula_pendente", 8),     # matrícula pendente: idem, sem disciplina ativa no momento
    ("inadimplente_cronico", 7),   # maioria dos boletos vencidos/em processamento
    ("quase_formando", 7),         # último período, histórico quase todo aprovado, estágio avançado
    ("padrao", 5),                  # caso médio, sem característica dominante
]
ARCHETYPE_LABELS = [a[0] for a in ARCHETYPES]
ARCHETYPE_WEIGHTS = [a[1] for a in ARCHETYPES]

# Pedagogia é o único curso com regras reais de Estágio Supervisionado Obrigatório
# (diretrizes FATECIE, seção 4): para a entrada 2025/1, a disciplina é
# disponibilizada no 7º semestre — sobrepõe a fórmula genérica dos demais cursos.
PEDAGOGIA_ELIGIBLE_PERIOD = 7

REJECTION_REASONS = [
    "período incompatível com a carga horária",
    "data de início inadequada",
    "documento sem anexo",
    "supervisor incorreto",
    "dados obrigatórios ausentes",
]

# Cenários de progresso no estágio para alunos de Pedagogia já elegíveis
# (diretrizes, seções 9, 28, 29, 32, 34) — cada um monta um conjunto coerente de
# InternshipRequirement/InternshipWaiver/InternshipFinalReport, nunca campos
# soltos sem sentido entre si.
INTERNSHIP_SCENARIOS = [
    ("not_started", 20),
    ("stage1_in_analysis", 12),
    ("stage1_formalized_stage2_not_requested", 12),
    ("stage1_rejected", 8),
    ("two_stages_formalized", 10),
    ("all_stages_in_progress", 10),
    ("waiver_professional_activity", 8),
    ("waiver_convalidation", 5),
    ("awaiting_final_report_submission", 5),
    ("final_report_submitted", 5),
    ("final_report_returned", 3),
    ("final_report_approved", 5),
    ("dependency", 2),
]
INTERNSHIP_SCENARIO_LABELS = [s[0] for s in INTERNSHIP_SCENARIOS]
INTERNSHIP_SCENARIO_WEIGHTS = [s[1] for s in INTERNSHIP_SCENARIOS]


def _pick_archetype() -> str:
    return random.choices(ARCHETYPE_LABELS, weights=ARCHETYPE_WEIGHTS, k=1)[0]


def _pick_internship_scenario() -> str:
    return random.choices(INTERNSHIP_SCENARIO_LABELS, weights=INTERNSHIP_SCENARIO_WEIGHTS, k=1)[0]


def _business_days_delta(base_date, business_days: int):
    """Soma/subtrai dias úteis (só pula fins de semana; sem feriados) a partir de base_date."""
    step = 1 if business_days >= 0 else -1
    remaining = abs(business_days)
    current = base_date
    while remaining > 0:
        current += timedelta(days=step)
        if current.weekday() < 5:
            remaining -= 1
    return current


def _group_by_period(subjects):
    by_period: dict[int, list] = {}
    for subject in subjects:
        by_period.setdefault(subject.period, []).append(subject)
    return by_period


class Command(BaseCommand):
    help = (
        "Popula a base demo da FATECE: cursos, disciplinas, alunos com cenários "
        "acadêmicos variados (documento, seções 3.1 e 4) e equipe de atendimento."
    )

    def add_arguments(self, parser):
        parser.add_argument("--students", type=int, default=10000)

    def handle(self, *args, **options):
        num_students = options["students"]
        self._num_students = num_students

        self.stdout.write("Limpando dados anteriores...")
        self._flush()

        self.stdout.write("Criando contas de equipe (atendente, admin)...")
        self._create_staff_accounts()

        self.stdout.write("Criando cursos e disciplinas...")
        courses = self._create_courses()
        subjects_by_course = self._create_subjects(courses)

        self.stdout.write(f"Gerando {num_students} alunos com cenários variados...")
        students, archetypes = self._create_students(courses, num_students)

        self.stdout.write("Gerando histórico de matrículas (períodos fechados e vigentes) e atividades...")
        self._create_enrollments_and_activities(students, archetypes, subjects_by_course)

        self.stdout.write("Gerando dados financeiros...")
        self._create_financial_records(students, archetypes)

        self.stdout.write("Gerando situação de estágio...")
        self._create_internship_data(students, courses, archetypes)

        self.stdout.write("Criando personas fixas para os cenários de demonstração...")
        self._create_demo_personas(courses, subjects_by_course)

        self.stdout.write(self.style.SUCCESS("Seed concluído."))
        self._print_demo_credentials()

    # ---- limpeza ----

    def _flush(self):
        # Apaga explicitamente na ordem de dependência (tickets/mensagens criados em
        # testes manuais não são cobertos com segurança pela cascata automática do
        # Django quando o volume de linhas é grande).
        AIExecution.objects.all().delete()
        ConversationScore.objects.all().delete()
        Occurrence.objects.all().delete()
        Evaluation.objects.all().delete()
        Message.objects.all().delete()
        Ticket.objects.all().delete()
        Activity.objects.all().delete()
        Enrollment.objects.all().delete()
        FinancialRecord.objects.all().delete()
        InternshipRequirement.objects.all().delete()
        InternshipWaiver.objects.all().delete()
        InternshipFinalReport.objects.all().delete()
        Student.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Subject.objects.all().delete()
        Course.objects.all().delete()

    # ---- equipe ----

    def _create_staff_accounts(self):
        password_hash = make_password(STAFF_PASSWORD)
        User.objects.get_or_create(
            username="admin.master",
            defaults=dict(
                first_name="Admin", last_name="UniFatecie", email="admin.master@fatece.edu.br",
                role=User.Role.ADMIN, password=password_hash, is_staff=True, is_superuser=True,
            ),
        )
        User.objects.create(
            username="yanka.machado", first_name="Yanka", last_name="Machado",
            email="yanka.machado@fatece.edu.br", role=User.Role.MONITOR, password=password_hash,
        )

    # ---- estrutura acadêmica ----

    def _create_courses(self):
        courses = []
        for name, code, total_periods in COURSES:
            eligible_period = (
                PEDAGOGIA_ELIGIBLE_PERIOD if code == "PED" else max(total_periods - 2, 3)
            )
            course = Course.objects.create(
                name=name, code=code, total_periods=total_periods,
                internship_eligible_period=eligible_period,
            )
            courses.append(course)
        return courses

    def _create_subjects(self, courses):
        subjects_by_course = {}
        for course in courses:
            subjects = []
            for period in range(1, course.total_periods + 1):
                count = 1 if period % 2 else 2
                for idx in range(count):
                    topic = random.choice(TOPICS)
                    subject = Subject.objects.create(
                        course=course,
                        name=f"{topic} {period}",
                        code=f"{course.code}{period}{idx}",
                        period=period,
                        workload=random.choice([40, 60, 80]),
                    )
                    subjects.append(subject)
            subjects_by_course[course.id] = subjects
        return subjects_by_course

    # ---- alunos ----

    def _period_for_archetype(self, archetype, total_periods):
        if archetype == "calouro":
            return 1
        if archetype == "quase_formando":
            return total_periods
        if archetype == "com_dependencia":
            return random.randint(2, total_periods)
        return random.randint(1, total_periods)

    def _academic_status_for_archetype(self, archetype):
        if archetype == "trancamento":
            return Student.AcademicStatus.LOCKED
        if archetype == "matricula_pendente":
            return Student.AcademicStatus.PENDING_ENROLLMENT
        return Student.AcademicStatus.REGULAR

    def _create_students(self, courses, num_students):
        ra_list = [f"FTC{100000 + i}" for i in range(num_students)]

        users = []
        for ra in ra_list:
            behavior_score = 100
            if random.random() < 0.04:
                behavior_score = random.randint(50, 90)
            users.append(User(
                username=ra, first_name=fake.first_name(), last_name=fake.last_name(),
                email=f"{ra}@fatece.edu.br", role=User.Role.STUDENT,
                password=make_password(ra), behavior_score=behavior_score,
            ))
        User.objects.bulk_create(users, batch_size=1000)
        users_by_ra = {u.username: u for u in User.objects.filter(role=User.Role.STUDENT)}

        students = []
        archetype_by_ra = {}
        for ra in ra_list:
            course = random.choice(courses)
            archetype = _pick_archetype()
            archetype_by_ra[ra] = archetype
            students.append(Student(
                user=users_by_ra[ra],
                ra=ra,
                course=course,
                current_period=self._period_for_archetype(archetype, course.total_periods),
                academic_status=self._academic_status_for_archetype(archetype),
            ))
        Student.objects.bulk_create(students, batch_size=1000)

        all_students = list(Student.objects.select_related("user", "course").all())
        archetype_by_student_id = {s.id: archetype_by_ra[s.ra] for s in all_students}
        return all_students, archetype_by_student_id

    def _create_enrollments_and_activities(self, students, archetypes, subjects_by_course):
        enrollments = []
        failed_subject_by_student: dict[int, object] = {}

        for student in students:
            archetype = archetypes[student.id]
            subjects_by_period = _group_by_period(subjects_by_course.get(student.course_id, []))
            has_current_enrollment = archetype not in ("trancamento", "matricula_pendente")

            # Períodos já encerrados: nota final definida (aprovado ou reprovado).
            for period in range(1, student.current_period):
                for subject in subjects_by_period.get(period, []):
                    if random.random() < 0.82:
                        status, grade = Enrollment.Status.PASSED, round(random.uniform(6.0, 10.0), 1)
                    else:
                        status, grade = Enrollment.Status.FAILED, round(random.uniform(1.0, 5.9), 1)
                        failed_subject_by_student.setdefault(student.id, subject)
                    enrollments.append(Enrollment(
                        student=student, subject=subject, period=period, status=status, grade=grade,
                    ))

            # Período vigente: matérias em andamento (sem nota ainda).
            if has_current_enrollment:
                for subject in subjects_by_period.get(student.current_period, []):
                    enrollments.append(Enrollment(
                        student=student, subject=subject, period=student.current_period,
                        status=Enrollment.Status.IN_PROGRESS, grade=None,
                    ))

                if archetype == "com_dependencia":
                    retake_subject = failed_subject_by_student.get(student.id)
                    if retake_subject is not None:
                        enrollments.append(Enrollment(
                            student=student, subject=retake_subject, period=student.current_period,
                            status=Enrollment.Status.IN_PROGRESS, grade=None,
                        ))

        Enrollment.objects.bulk_create(enrollments, batch_size=2000, ignore_conflicts=True)

        activities = []
        today = timezone.now().date()
        in_progress = Enrollment.objects.filter(
            status=Enrollment.Status.IN_PROGRESS
        ).select_related("student", "subject")
        for enrollment in in_progress:
            for n in range(random.randint(1, 2)):
                due = today + timedelta(days=random.randint(-20, 20))
                if due < today:
                    status = random.choice(
                        [Activity.Status.LATE] * 3 + [Activity.Status.SUBMITTED] * 4
                        + [Activity.Status.GRADED] * 3
                    )
                else:
                    status = random.choice(
                        [Activity.Status.PENDING] * 7 + [Activity.Status.SUBMITTED] * 3
                    )
                activities.append(Activity(
                    student=enrollment.student, subject=enrollment.subject,
                    title=f"Atividade {n + 1} - {enrollment.subject.name}",
                    due_date=due, status=status,
                ))
        Activity.objects.bulk_create(activities, batch_size=2000)

    def _create_financial_records(self, students, archetypes):
        records = []
        today = timezone.now().date()
        for student in students:
            chronic = archetypes[student.id] == "inadimplente_cronico"
            for months_ago in range(5, -1, -1):
                ref_month = (today.replace(day=1) - timedelta(days=months_ago * 30)).replace(day=1)
                due = ref_month.replace(day=10)
                if chronic:
                    status = random.choice(
                        [FinancialRecord.Status.OVERDUE] * 6 + [FinancialRecord.Status.PROCESSING] * 2
                        + [FinancialRecord.Status.PAID] * 2
                    )
                elif months_ago == 0:
                    status = random.choice(
                        [FinancialRecord.Status.PENDING] * 5 + [FinancialRecord.Status.OVERDUE] * 3
                        + [FinancialRecord.Status.PROCESSING] * 2
                    )
                else:
                    status = random.choice(
                        [FinancialRecord.Status.PAID] * 8 + [FinancialRecord.Status.OVERDUE] * 2
                    )
                paid_at = None
                if status == FinancialRecord.Status.PAID:
                    paid_at = timezone.make_aware(datetime.combine(due, datetime.min.time()))
                records.append(FinancialRecord(
                    student=student, reference_month=ref_month, amount=round(random.uniform(350, 950), 2),
                    due_date=due, status=status, paid_at=paid_at,
                    barcode="".join(random.choices("0123456789", k=44)),
                ))
        FinancialRecord.objects.bulk_create(records, batch_size=2000)

    def _create_internship_data(self, students, courses, archetypes):
        pedagogia = next((c for c in courses if c.code == "PED"), None)
        requirements = []
        waivers = []
        final_reports = []
        today = timezone.now().date()

        for student in students:
            if pedagogia is None or student.course_id != pedagogia.id:
                continue
            if student.current_period < PEDAGOGIA_ELIGIBLE_PERIOD:
                continue

            scenario = _pick_internship_scenario()
            requirements.extend(self._internship_requirements_for_scenario(student, scenario, today))
            waiver = self._internship_waiver_for_scenario(student, scenario)
            if waiver:
                waivers.append(waiver)
            final_report = self._internship_final_report_for_scenario(student, scenario, today)
            if final_report:
                final_reports.append(final_report)

        InternshipRequirement.objects.bulk_create(requirements, batch_size=2000)
        InternshipWaiver.objects.bulk_create(waivers, batch_size=2000)
        InternshipFinalReport.objects.bulk_create(final_reports, batch_size=2000)

    def _host_institution(self):
        return f"{fake.company()} - Unidade Escolar"

    def _internship_requirements_for_scenario(self, student, scenario, today):
        stage0, stage1, stage2 = STAGE_ORDER

        def formalized(stage, protocol_days_ago):
            protocol_date = today - timedelta(days=protocol_days_ago)
            decision_date = _business_days_delta(protocol_date, 7)
            return InternshipRequirement(
                student=student, stage=stage, status=InternshipRequirement.Status.FORMALIZED,
                host_institution=self._host_institution(), protocol_date=protocol_date,
                decision_date=decision_date, planned_start_date=decision_date,
            )

        def completed(stage, protocol_days_ago):
            req = formalized(stage, protocol_days_ago)
            req.status = InternshipRequirement.Status.COMPLETED
            return req

        def in_analysis(stage, protocol_days_ago):
            protocol_date = today - timedelta(days=protocol_days_ago)
            return InternshipRequirement(
                student=student, stage=stage, status=InternshipRequirement.Status.IN_ANALYSIS,
                host_institution=self._host_institution(), protocol_date=protocol_date,
                planned_start_date=_business_days_delta(protocol_date, 7),
            )

        def rejected(stage, protocol_days_ago):
            protocol_date = today - timedelta(days=protocol_days_ago)
            return InternshipRequirement(
                student=student, stage=stage, status=InternshipRequirement.Status.REJECTED,
                host_institution=self._host_institution(), protocol_date=protocol_date,
                decision_date=_business_days_delta(protocol_date, 7),
                rejection_reason=random.choice(REJECTION_REASONS),
            )

        if scenario == "stage1_in_analysis":
            return [in_analysis(stage0, random.randint(1, 6))]
        if scenario == "stage1_formalized_stage2_not_requested":
            return [formalized(stage0, random.randint(20, 40))]
        if scenario == "stage1_rejected":
            return [rejected(stage0, random.randint(15, 30))]
        if scenario == "two_stages_formalized":
            return [formalized(stage0, random.randint(40, 60)), formalized(stage1, random.randint(15, 30))]
        if scenario in ("all_stages_in_progress", "waiver_professional_activity", "waiver_convalidation"):
            return [
                formalized(stage0, random.randint(60, 80)),
                formalized(stage1, random.randint(35, 55)),
                formalized(stage2, random.randint(10, 25)),
            ]
        if scenario in (
            "awaiting_final_report_submission", "final_report_submitted",
            "final_report_returned", "final_report_approved",
        ):
            return [
                completed(stage0, random.randint(90, 120)),
                completed(stage1, random.randint(60, 89)),
                completed(stage2, random.randint(30, 59)),
            ]
        if scenario == "dependency":
            # Etapa de Gestão nunca foi solicitada: a disciplina encerrou sem conclusão.
            return [completed(stage0, random.randint(90, 120)), formalized(stage1, random.randint(60, 89))]
        return []  # "not_started": nenhum requerimento aberto ainda

    def _internship_waiver_for_scenario(self, student, scenario):
        if scenario == "waiver_professional_activity":
            pct = random.choice([20, 50])
            remaining = round(96 * (1 - pct / 100))
            return InternshipWaiver(
                student=student, kind=InternshipWaiver.Kind.PROFESSIONAL_ACTIVITY,
                status=InternshipWaiver.Status.APPROVED,
                protocol_number=f"DISP-{random.randint(10000, 99999)}",
                approved_percentage=pct, remaining_hours=remaining,
                notes="Redução deferida por atividade profissional comprovada na área.",
            )
        if scenario == "waiver_convalidation":
            return InternshipWaiver(
                student=student, kind=InternshipWaiver.Kind.NON_MANDATORY_CONVALIDATION,
                status=InternshipWaiver.Status.APPROVED,
                protocol_number=f"CONV-{random.randint(10000, 99999)}",
                approved_percentage=75, remaining_hours=36,
                notes="Convalidação de estágio não obrigatório/remunerado já concluído.",
            )
        return None

    def _internship_final_report_for_scenario(self, student, scenario, today):
        if scenario == "awaiting_final_report_submission":
            return InternshipFinalReport(
                student=student, status=InternshipFinalReport.Status.NOT_SUBMITTED,
                discipline_term_ends_at=today + timedelta(days=random.randint(20, 60)),
            )
        if scenario == "final_report_submitted":
            return InternshipFinalReport(
                student=student, status=InternshipFinalReport.Status.SUBMITTED,
                submitted_at=today - timedelta(days=random.randint(5, 14)),
                discipline_term_ends_at=today - timedelta(days=random.randint(1, 6)),
            )
        if scenario == "final_report_returned":
            return InternshipFinalReport(
                student=student, status=InternshipFinalReport.Status.RETURNED_FOR_CORRECTION,
                submitted_at=today - timedelta(days=random.randint(20, 35)),
                discipline_term_ends_at=today - timedelta(days=random.randint(10, 20)),
                feedback="Faltou anexar a Ficha de Frequência da etapa de Gestão Escolar dentro do PDF único.",
            )
        if scenario == "final_report_approved":
            return InternshipFinalReport(
                student=student, status=InternshipFinalReport.Status.APPROVED,
                submitted_at=today - timedelta(days=random.randint(40, 60)),
                discipline_term_ends_at=today - timedelta(days=random.randint(35, 55)),
            )
        if scenario == "dependency":
            return InternshipFinalReport(
                student=student, status=InternshipFinalReport.Status.DEPENDENCY,
                discipline_term_ends_at=today - timedelta(days=random.randint(30, 90)),
                feedback=(
                    "Disciplina encerrada sem conclusão. Próxima solicitação de DP "
                    "prevista para fevereiro de 2027."
                ),
            )
        return None

    # ---- personas fixas (login e senha = RA, igual aos demais alunos) ----

    def _create_demo_personas(self, courses, subjects_by_course):
        pedagogia = next(c for c in courses if c.code == "PED")

        # Personas fixas cobrindo os cenários do Golden Dataset de estágio de
        # Pedagogia (apps/ai/golden_dataset.py) — cada uma isolada por design,
        # nunca sorteada, para que os testes sejam sempre reprodutíveis.
        self._personas = [
            dict(ra="FTC900000", first="Regular", last="Exemplo",
                 note="elegível, sem requerimento aberto ainda",
                 period=7, status=Student.AcademicStatus.REGULAR, behavior=100),
            dict(ra="FTC900001", first="Estagio", last="EmAnalise",
                 note="1ª etapa (Educação Infantil) em análise",
                 period=7, status=Student.AcademicStatus.REGULAR, behavior=100),
            dict(ra="FTC900002", first="Estagio", last="ComDispensa",
                 note="dispensa por atividade profissional deferida (50%, 48h restantes)",
                 period=7, status=Student.AcademicStatus.REGULAR, behavior=100),
            dict(ra="FTC900003", first="Estagio", last="RelatorioEnviado",
                 note="3 etapas concluídas, relatório final enviado, aguardando correção",
                 period=8, status=Student.AcademicStatus.REGULAR, behavior=100),
            dict(ra="FTC900004", first="Estagio", last="NaoElegivel",
                 note="ainda não chegou ao 7º período (fora do período de estágio)",
                 period=4, status=Student.AcademicStatus.REGULAR, behavior=100),
            dict(ra="FTC900005", first="Reincidente", last="Linguagem",
                 note="score reduzido por reincidência em linguagem",
                 period=7, status=Student.AcademicStatus.REGULAR, behavior=62),
        ]

        created = {}
        for p in self._personas:
            user = User.objects.create(
                username=p["ra"], first_name=p["first"], last_name=p["last"],
                email=f"{p['ra']}@fatece.edu.br", role=User.Role.STUDENT,
                password=make_password(p["ra"]), behavior_score=p["behavior"],
            )
            student = Student.objects.create(
                user=user, ra=p["ra"], course=pedagogia,
                current_period=p["period"], academic_status=p["status"],
            )
            created[p["ra"]] = student

        today = timezone.now().date()
        stage0, stage1, _stage2 = STAGE_ORDER

        em_analise = created["FTC900001"]
        protocol_date = today - timedelta(days=3)
        InternshipRequirement.objects.create(
            student=em_analise, stage=stage0, status=InternshipRequirement.Status.IN_ANALYSIS,
            host_institution=self._host_institution(), protocol_date=protocol_date,
            planned_start_date=_business_days_delta(protocol_date, 7),
        )

        com_dispensa = created["FTC900002"]
        for stage, days_ago in ((stage0, 70), (stage1, 45)):
            self._create_formalized_requirement(com_dispensa, stage, days_ago, today)
        InternshipWaiver.objects.create(
            student=com_dispensa, kind=InternshipWaiver.Kind.PROFESSIONAL_ACTIVITY,
            status=InternshipWaiver.Status.APPROVED, protocol_number="DISP-90001",
            approved_percentage=50, remaining_hours=48,
            notes="Redução deferida por atividade profissional comprovada na área.",
        )

        relatorio_enviado = created["FTC900003"]
        for stage, days_ago in ((stage0, 110), (stage1, 80), (STAGE_ORDER[2], 50)):
            req = self._create_formalized_requirement(relatorio_enviado, stage, days_ago, today)
            req.status = InternshipRequirement.Status.COMPLETED
            req.save(update_fields=["status"])
        InternshipFinalReport.objects.create(
            student=relatorio_enviado, status=InternshipFinalReport.Status.SUBMITTED,
            submitted_at=today - timedelta(days=8),
            discipline_term_ends_at=today - timedelta(days=3),
        )

    def _create_formalized_requirement(self, student, stage, protocol_days_ago, today):
        protocol_date = today - timedelta(days=protocol_days_ago)
        decision_date = _business_days_delta(protocol_date, 7)
        return InternshipRequirement.objects.create(
            student=student, stage=stage, status=InternshipRequirement.Status.FORMALIZED,
            host_institution=self._host_institution(), protocol_date=protocol_date,
            decision_date=decision_date, planned_start_date=decision_date,
        )

    def _print_demo_credentials(self):
        last_ra = f"FTC{100000 + self._num_students - 1}"
        self.stdout.write("\nCredenciais de demonstração:")
        self.stdout.write("  Alunos -> usuário e senha = o próprio RA")
        for p in self._personas:
            self.stdout.write(f"    - {p['ra']}  ({p['note']})")
        self.stdout.write(f"    - demais alunos: FTC100000 até {last_ra} (usuário e senha = o RA)")
        self.stdout.write("\n  Equipe -> senha = demo123")
        self.stdout.write("    - yanka.machado (atendente)")
        self.stdout.write("    - admin.master (administrador / superuser)")
