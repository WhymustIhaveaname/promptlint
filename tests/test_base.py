"""Tests for BaseRule interface and validation."""

import pytest
from pathlib import Path

from promptlint.rules.base import BaseRule, RuleConfig, RuleContext, RuleType, Violation


def test_violation_defaults():
    v = Violation(rule_id="test", message="msg")
    assert v.severity == "error"
    assert v.line is None
    assert v.snippet is None


def test_rule_config_defaults():
    cfg = RuleConfig()
    assert cfg.enabled is True
    assert cfg.severity == "error"
    assert cfg.params == {}


def test_rule_context_defaults():
    ctx = RuleContext()
    assert ctx.scan_path is None


def test_rule_type_enum():
    assert RuleType.HARDCODED.value == "hardcoded"
    assert RuleType.LLM_INTERPRET.value == "llm_interpret"
    assert RuleType.LLM_RESPONSE.value == "llm_response"


def test_subclass_missing_rule_id():
    with pytest.raises(TypeError, match="must set a non-empty 'rule_id'"):
        class BadRule(BaseRule):
            description = "has desc"
            def check(self, content, file_path, ctx=None):
                return []


def test_subclass_missing_description():
    with pytest.raises(TypeError, match="must set a non-empty 'description'"):
        class BadRule(BaseRule):
            rule_id = "has_id"
            def check(self, content, file_path, ctx=None):
                return []


def test_subclass_valid():
    class GoodRule(BaseRule):
        rule_id = "good"
        description = "A good rule"
        def check(self, content, file_path, ctx=None):
            return []

    rule = GoodRule()
    assert rule.rule_id == "good"
    assert rule.config.severity == "error"
