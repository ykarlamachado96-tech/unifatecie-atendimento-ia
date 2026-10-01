from apps.integrations.connectors import get_connector
from apps.internship.models import STAGE_ORDER, InternshipFinalReport, InternshipRequirement


def test_student_below_eligible_period_is_not_eligible(make_student):
    student = make_student(period=5)  # curso exige período 7
    overview = get_connector().get_student_internship_status(student.id)
    assert overview["status"] == "NOT_ELIGIBLE"
    assert overview["is_eligible"] is False


def test_eligible_student_without_requirements_is_not_started(student):
    overview = get_connector().get_student_internship_status(student.id)
    assert overview["status"] == "NOT_STARTED"
    assert overview["next_requestable_stage"] == STAGE_ORDER[0]


def test_stage_in_analysis_blocks_next_requestable_stage(student):
    InternshipRequirement.objects.create(
        student=student, stage=STAGE_ORDER[0], status=InternshipRequirement.Status.IN_ANALYSIS,
    )

    overview = get_connector().get_student_internship_status(student.id)

    assert overview["status"] == "AWAITING_ANALYSIS"
    assert overview["has_active_requirement_in_analysis"] is True
    assert overview["next_requestable_stage"] is None


def test_formalized_stage_releases_next_stage(student):
    InternshipRequirement.objects.create(
        student=student, stage=STAGE_ORDER[0], status=InternshipRequirement.Status.FORMALIZED,
    )

    overview = get_connector().get_student_internship_status(student.id)

    assert overview["status"] == "IN_PROGRESS"
    assert overview["next_requestable_stage"] == STAGE_ORDER[1]


def test_approved_final_report_means_completed(student):
    for stage in STAGE_ORDER:
        InternshipRequirement.objects.create(
            student=student, stage=stage, status=InternshipRequirement.Status.COMPLETED,
        )
    InternshipFinalReport.objects.create(student=student, status=InternshipFinalReport.Status.APPROVED)

    overview = get_connector().get_student_internship_status(student.id)

    assert overview["status"] == "COMPLETED"


def test_waiver_percentage_and_hours_come_from_the_individual_protocol(student):
    from apps.internship.models import InternshipWaiver

    InternshipWaiver.objects.create(
        student=student, kind=InternshipWaiver.Kind.PROFESSIONAL_ACTIVITY,
        status=InternshipWaiver.Status.APPROVED, protocol_number="DISP-1",
        approved_percentage=50, remaining_hours=48,
    )

    overview = get_connector().get_student_internship_status(student.id)

    assert overview["active_waiver"]["approved_percentage"] == 50
    assert overview["active_waiver"]["remaining_hours"] == 48
