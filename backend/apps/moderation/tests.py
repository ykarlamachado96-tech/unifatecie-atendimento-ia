from apps.moderation import service


def test_clean_text_not_flagged():
    result = service.check("Quero saber sobre a carga horária da etapa de Gestão Escolar.")
    assert result.flagged is False
    assert result.status == "CLEAN"
    assert result.sanitized_text == "Quero saber sobre a carga horária da etapa de Gestão Escolar."


def test_profanity_is_masked_not_blocked():
    result = service.check("Isso é uma merda de sistema, não funciona nada!")
    assert result.flagged is True
    assert result.status == "MASKED"
    assert result.category == "PROFANITY"
    assert "merda" not in result.sanitized_text.lower()


def test_insult_is_masked():
    result = service.check("Vocês são uns idiotas, ninguém resolve nada aqui.")
    assert result.flagged is True
    assert result.status == "MASKED"
    assert result.category == "INSULT"
    assert "idiotas" not in result.sanitized_text.lower()


def test_threat_is_blocked_not_just_masked():
    result = service.check("Vou te matar se isso não for resolvido agora.")
    assert result.flagged is True
    assert result.status == "BLOCKED"
    assert result.category == "THREAT"


def test_only_matched_terms_are_masked_rest_of_message_kept():
    result = service.check("Essa porra de sistema travou de novo, pode me ajudar?")
    assert "pode me ajudar" in result.sanitized_text
