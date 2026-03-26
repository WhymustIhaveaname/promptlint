"""Tests for BaseRule interface and validation."""

import pytest
from pathlib import Path

from promptlint.rules_hardcode.base import BaseRule, RuleConfig, RuleContext, RuleType, Violation


def test_violation_defaults():
    v = Violation(rule_id="test", message="msg")
    assert v.severity == "error"
    assert v.line is None
    assert v.snippet is None


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
