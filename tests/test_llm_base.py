"""Tests for LLM rule loading and response parsing."""

import json
from pathlib import Path

import pytest

from promptlint.rules_hardcode.base import RuleConfig
from promptlint.rules_llm.llm_base import LLMRule, _parse_rule_md, discover_llm_rules


# --- _parse_rule_md ---

def _write_rule_md(tmp_path, content):
    p = tmp_path / "test_rule.md"
    p.write_text(content, encoding="utf-8")
    return p


class TestParseRuleMd:
    def test_basic(self, tmp_path):
        md = _write_rule_md(tmp_path, """\
---
rule_id: my_rule
---

# my_rule — Some title

This is the description.

## Examples

❌ bad example
✅ good example
""")
        result = _parse_rule_md(md)
        assert result["rule_id"] == "my_rule"
        # rule_md is the raw body after frontmatter, not parsed
        assert "This is the description." in result["rule_md"]
        assert "❌ bad example" in result["rule_md"]
        assert "Some title" in result["rule_md"]

    def test_no_examples_section(self, tmp_path):
        md = _write_rule_md(tmp_path, """\
---
rule_id: no_examples
---

# no_examples — Title

Just a description, no examples section.
""")
        result = _parse_rule_md(md)
        assert result["rule_id"] == "no_examples"
        assert "Just a description" in result["rule_md"]

    def test_missing_frontmatter_raises(self, tmp_path):
        md = _write_rule_md(tmp_path, "# No frontmatter here\nJust text.")
        with pytest.raises(ValueError, match="missing YAML frontmatter"):
            _parse_rule_md(md)


# --- _parse_response ---

class TestParseResponse:
    """Test LLMRule._parse_response without calling any LLM."""

    def _make_rule(self):
        rule = LLMRule.__new__(LLMRule)
        rule.rule_id = "test_rule"
        rule.config = RuleConfig(severity="warn")
        return rule

    def test_valid_json_array(self):
        rule = self._make_rule()
        text = json.dumps([{"message": "问题", "snippet": "foo", "line": 3}])
        violations = rule._parse_response(text)
        assert len(violations) == 1
        assert violations[0].message == "问题"
        assert violations[0].line == 3
        assert violations[0].severity == "warn"

    def test_empty_array(self):
        rule = self._make_rule()
        assert rule._parse_response("[]") == []

    def test_markdown_code_block(self):
        rule = self._make_rule()
        text = '```json\n[{"message": "问题", "snippet": "x", "line": 1}]\n```'
        violations = rule._parse_response(text)
        assert len(violations) == 1

    def test_truncated_json_recovery(self):
        rule = self._make_rule()
        # JSON cut off before closing bracket
        text = '[{"message": "问题", "snippet": "x", "line": 1}'
        violations = rule._parse_response(text)
        assert len(violations) == 1

    def test_completely_invalid_json(self):
        rule = self._make_rule()
        assert rule._parse_response("this is not json at all") == []

    def test_non_list_response(self):
        rule = self._make_rule()
        assert rule._parse_response('{"message": "single object"}') == []

    def test_non_dict_items_skipped(self):
        rule = self._make_rule()
        text = json.dumps([{"message": "ok"}, "not a dict", 42])
        violations = rule._parse_response(text)
        assert len(violations) == 1

    def test_snippet_truncated_at_120(self):
        rule = self._make_rule()
        long_snippet = "x" * 200
        text = json.dumps([{"message": "m", "snippet": long_snippet}])
        violations = rule._parse_response(text)
        assert len(violations[0].snippet) == 120

    def test_missing_message_uses_default(self):
        rule = self._make_rule()
        text = json.dumps([{"snippet": "foo"}])
        violations = rule._parse_response(text)
        assert violations[0].message == "LLM-detected violation"


# --- discover_llm_rules ---

class TestDiscoverLlmRules:
    def test_finds_builtin_llm_rules(self):
        rules = discover_llm_rules()
        assert "hollow_instructions" in rules
        assert "contradictory_instructions" in rules
        assert len(rules) == 7

    def test_malformed_md_skipped(self, tmp_path, monkeypatch):
        """A bad .md file should be skipped, not crash discovery."""
        bad = tmp_path / "broken.md"
        bad.write_text("no frontmatter here", encoding="utf-8")
        good = tmp_path / "good.md"
        good.write_text("---\nrule_id: good\n---\n\nDescription.\n", encoding="utf-8")

        monkeypatch.setattr("promptlint.rules_llm.llm_base.LLM_RULES_DIR", tmp_path)
        rules = discover_llm_rules()
        assert "good" in rules
        assert len(rules) == 1
