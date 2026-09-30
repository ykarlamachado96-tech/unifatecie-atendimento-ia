export interface CurrentSubject {
  subject_code: string;
  subject_name: string;
  period: number;
  status: string;
  grade: number | null;
}

export interface PendingActivity {
  subject_code: string;
  title: string;
  due_date: string;
  status: "PENDING" | "LATE";
}

export interface FinancialStatus {
  has_overdue: boolean;
  total_overdue: number;
  records_count: number;
}

export interface OpenInvoice {
  invoice_id: number;
  reference_month: string;
  amount: number;
  due_date: string;
  status: string;
}

export interface InternshipStage {
  stage: string;
  stage_label: string;
  required_hours: number;
  status: string;
  host_institution: string;
  protocol_date: string | null;
  decision_date: string | null;
  planned_start_date: string | null;
  rejection_reason: string;
}

export interface InternshipWaiver {
  kind: string;
  protocol_number: string;
  approved_percentage: number | null;
  remaining_hours: number | null;
  notes: string;
}

export interface InternshipFinalReport {
  status: string;
  submitted_at: string | null;
  discipline_term_ends_at: string | null;
  feedback: string;
}

export interface InternshipStatus {
  status: string;
  overall_status: string;
  is_eligible: boolean;
  eligible_from_period: number;
  current_period: number;
  stages: InternshipStage[];
  total_hours_required: number;
  next_requestable_stage: string | null;
  has_active_requirement_in_analysis: boolean;
  active_waiver: InternshipWaiver | null;
  final_report: InternshipFinalReport;
}

export interface AcademicSummary {
  ra: string;
  course: string;
  current_period: number;
  academic_status: string;
  current_subjects: CurrentSubject[];
  pending_activities: PendingActivity[];
  financial_status: FinancialStatus;
  open_invoices: OpenInvoice[];
  internship_status: InternshipStatus;
}

export type TicketStatus =
  | "OPEN"
  | "AI_PROCESSING"
  | "AI_WAITING_USER"
  | "WAITING_HUMAN"
  | "HUMAN_ASSIGNED"
  | "HUMAN_PROCESSING"
  | "RESOLVED"
  | "CLOSED";

export interface Ticket {
  id: number;
  student: number;
  student_ra: string;
  student_name: string;
  status: TicketStatus;
  intent: string;
  assigned_monitor: number | null;
  resolved_by: "AI" | "HUMAN" | null;
  created_at: string;
  closed_at: string | null;
}

export interface HandoffContext {
  setor: string | null;
  assunto: string | null;
  resumo: string | null;
  summary: string;
  intent: string | null;
  tools_used: string[];
  data_consulted: unknown;
  reason: string;
  suggested_next_step: string;
}

export interface TicketDetail extends Ticket {
  handoff_context: HandoffContext | null;
  messages: Message[];
}

export type SenderType = "STUDENT" | "MONITOR" | "AI" | "SYSTEM";

export interface Message {
  id: number;
  ticket: number;
  sender: number | null;
  sender_type: SenderType;
  displayed_content: string;
  moderation_status: "CLEAN" | "MASKED" | "BLOCKED";
  created_at: string;
}

export type EvaluationStatus = "PENDING" | "SUBMITTED" | "AUTO_TIMEOUT";

export interface Evaluation {
  id: number;
  ticket: number;
  student: number;
  monitor: number | null;
  stars: number | null;
  comment: string;
  status: EvaluationStatus;
  created_at: string;
  deadline_at: string;
  submitted_at: string | null;
}

