"""Tests for built-in rules."""

from pathlib import Path

from promptlint.rules.base import RuleConfig
from promptlint.rules.max_lines import MaxLinesRule
from promptlint.rules.path_exists import PathExistsRule


class TestMaxLines:
    def test_under_limit(self):
        rule = MaxLinesRule(RuleConfig(params={"max": 10}))
        violations = rule.check("line1\nline2\nline3", Path("test.md"))
        assert violations == []

    def test_at_limit(self):
        content = "\n".join(f"line{i}" for i in range(10))
        rule = MaxLinesRule(RuleConfig(params={"max": 10}))
        assert rule.check(content, Path("test.md")) == []

    def test_over_limit(self):
        content = "\n".join(f"line{i}" for i in range(11))
        rule = MaxLinesRule(RuleConfig(params={"max": 10}))
        violations = rule.check(content, Path("test.md"))
        assert len(violations) == 1
        assert "11 lines" in violations[0].message
        assert "max 10" in violations[0].message

    def test_default_max_500(self):
        rule = MaxLinesRule()
        assert rule.max == 500

    def test_uses_config_severity(self):
        rule = MaxLinesRule(RuleConfig(severity="warn", params={"max": 1}))
        violations = rule.check("a\nb\nc", Path("test.md"))
        assert violations[0].severity == "warn"

    def test_trailing_newline_not_counted_as_extra_line(self):
        """'hello\\n' should be 1 line, not 2."""
        rule = MaxLinesRule(RuleConfig(params={"max": 1}))
        assert rule.check("hello\n", Path("test.md")) == []


class TestPathExists:
    def test_no_paths(self):
        rule = PathExistsRule()
        violations = rule.check("No paths here.", Path("test.md"))
        assert violations == []

    def test_existing_path(self, tmp_path):
        (tmp_path / "sub" / "dir").mkdir(parents=True)
        (tmp_path / "sub" / "dir" / "file.txt").touch()
        path = str(tmp_path / "sub" / "dir" / "file.txt")
        rule = PathExistsRule()
        violations = rule.check(f"See {path}", Path("test.md"))
        assert violations == []

    def test_missing_path(self):
        rule = PathExistsRule()
        violations = rule.check("See /nonexistent/deep/nested/file.txt", Path("test.md"))
        assert len(violations) == 1
        assert "/nonexistent/deep/nested/file.txt" in violations[0].message

    def test_url_paths_skipped(self):
        rule = PathExistsRule()
        content = "Visit https://example.com/api/v1/users for docs"
        violations = rule.check(content, Path("test.md"))
        assert violations == []

    def test_deduplication(self):
        """Same path on multiple lines should only report once."""
        rule = PathExistsRule()
        content = "/no/such/path/file.txt\n/no/such/path/file.txt"
        violations = rule.check(content, Path("test.md"))
        assert len(violations) == 1

    def test_line_number_reported(self):
        rule = PathExistsRule()
        content = "line1\n/no/such/path/file.txt"
        violations = rule.check(content, Path("test.md"))
        assert violations[0].line == 2

    def test_uses_config_severity(self):
        rule = PathExistsRule(RuleConfig(severity="info"))
        violations = rule.check("/no/such/path/file.txt", Path("test.md"))
        assert violations[0].severity == "info"
