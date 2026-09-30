import re
from dataclasses import dataclass, field

from .models import Occurrence

VALIDATOR_VERSION = "regex-v1"

SCORE_DECAY = {
    Occurrence.Category.PROFANITY: 2,
    Occurrence.Category.INSULT: 5,
    Occurrence.Category.THREAT: 20,
    Occurrence.Category.DISCRIMINATION: 20,
    Occurrence.Category.HARASSMENT: 8,
}
REINCIDENCE_EXTRA_DECAY = 8

# Listas simples PT-BR. Suficientes para o MVP; pensadas para expansão futura
# (o campo validator_version já permite trocar por um classificador de IA sem migração).
PROFANITY_TERMS = [
    r"\bmerda\b", r"\bporra\b", r"\bcaralho\b", r"\bcacete\b", r"\bbosta\b",
    r"\bfoda\b", r"\bfdp\b", r"\bputa\b",
]
INSULT_TERMS = [
    r"\bidiota\b", r"\bimbecil\b", r"\bburro\b", r"\bburra\b", r"\bin[uú]til\b",
    r"\bretardado\b", r"\bretardada\b", r"\bvagabundo\b", r"\bvagabunda\b",
    r"\botário\b", r"\botaria\b", r"\bin[cç]ompetente\b",
]
THREAT_TERMS = [
    r"\bvou te matar\b", r"\bvou (te )?bater\b", r"\bcuidado com voc[eê]\b",
    r"\bvai se arrepender\b", r"\bvou (te )?destruir\b", r"\bameaç",
]
DISCRIMINATION_TERMS = [
    r"\bracis", r"\bnegro de merda\b", r"\bviad[oa]\b", r"\bsapatão\b",
    r"\bretardado mental\b", r"\bpreconceit",
]
HARASSMENT_TERMS = [
    r"\bvou (te )?procurar\b", r"\bsei onde voc[eê] mora\b", r"\bvou (te )?perseguir\b",
    r"\bpara de me ignorar\b.*\bou\b",
]

CATEGORY_PATTERNS = [
    (Occurrence.Category.THREAT, THREAT_TERMS, Occurrence.Severity.CRITICAL),
    (Occurrence.Category.DISCRIMINATION, DISCRIMINATION_TERMS, Occurrence.Severity.CRITICAL),
    (Occurrence.Category.HARASSMENT, HARASSMENT_TERMS, Occurrence.Severity.HIGH),
    (Occurrence.Category.INSULT, INSULT_TERMS, Occurrence.Severity.MEDIUM),
    (Occurrence.Category.PROFANITY, PROFANITY_TERMS, Occurrence.Severity.LOW),
]


@dataclass
class ModerationResult:
    flagged: bool
    status: str  # Message.ModerationStatus
    sanitized_text: str
    category: str | None = None
    severity: str | None = None
    matched_terms: list[str] = field(default_factory=list)


def check(text: str) -> ModerationResult:
    lowered = text.lower()
    hits = []  # (category, severity, patterns_matched)
    all_matched_patterns = []
    for category, patterns, severity in CATEGORY_PATTERNS:
        matches = [p for p in patterns if re.search(p, lowered, flags=re.IGNORECASE)]
        if matches:
            hits.append((category, severity, matches))
            all_matched_patterns.extend(matches)

    if not hits:
        return ModerationResult(flagged=False, status="CLEAN", sanitized_text=text)

    # a ocorrência é registrada com a categoria de maior severidade encontrada,
    # mas TODOS os termos flagrados na mensagem são mascarados.
    severity_order = {
        Occurrence.Severity.CRITICAL: 3, Occurrence.Severity.HIGH: 2,
        Occurrence.Severity.MEDIUM: 1, Occurrence.Severity.LOW: 0,
    }
    hits.sort(key=lambda h: severity_order[h[1]], reverse=True)
    top_category, top_severity, _ = hits[0]

    sanitized = _mask(text, all_matched_patterns)
    status = "BLOCKED" if top_severity == Occurrence.Severity.CRITICAL else "MASKED"
    return ModerationResult(
        flagged=True, status=status, sanitized_text=sanitized,
        category=top_category, severity=top_severity, matched_terms=all_matched_patterns,
    )


def _mask(text: str, patterns: list[str]) -> str:
    masked = text
    for pattern in patterns:
        masked = re.sub(pattern, lambda m: "*" * len(m.group(0)), masked, flags=re.IGNORECASE)
    return masked


def register_occurrence(*, user, role, ticket, message, result: ModerationResult) -> Occurrence:
    occurrence = Occurrence.objects.create(
        user=user, role=role, ticket=ticket, message=message,
        category=result.category, severity=result.severity,
        original_message=message.original_content, sanitized_message=result.sanitized_text,
        validator_version=VALIDATOR_VERSION,
    )
    _apply_behavior_decay(user, result.category)
    return occurrence


def _apply_behavior_decay(user, category: str) -> None:
    decay = SCORE_DECAY.get(category, 0)
    is_reincident = Occurrence.objects.filter(user=user, category=category).count() > 1
    if is_reincident:
        decay += REINCIDENCE_EXTRA_DECAY
    user.refresh_from_db(fields=["behavior_score"])
    new_score = max(0, user.behavior_score - decay)
    type(user).objects.filter(pk=user.pk).update(behavior_score=new_score)
    user.behavior_score = new_score
