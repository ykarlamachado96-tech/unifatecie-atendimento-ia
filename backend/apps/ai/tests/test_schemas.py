import pytest
from pydantic import ValidationError

from apps.ai.schemas import IntentDecision


def test_tool_args_defaults_to_empty_dict_when_none():
    decision = IntentDecision.model_validate({
        "intent": "x", "confidence": 0.5, "requires_tool": False, "tool": None,
        "tool_args": None, "requires_human": False, "reason": None,
    })
    assert decision.tool_args == {}


def test_tool_args_defaults_to_empty_dict_when_omitted():
    decision = IntentDecision.model_validate({"intent": "x", "confidence": 0.5})
    assert decision.tool_args == {}


def test_confidence_out_of_range_is_rejected():
    with pytest.raises(ValidationError):
        IntentDecision.model_validate({"intent": "x", "confidence": 1.5})
