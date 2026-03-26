"""Tests for LLM backend: resolve_backends."""

from unittest.mock import patch

from promptlint.llm import resolve_backends


class TestResolveBackends:
    def test_auto_finds_claude(self):
        with patch("promptlint.llm.shutil.which", side_effect=lambda x: "/usr/bin/claude" if x == "claude" else None):
            assert resolve_backends(["auto"]) == ["claude"]

    def test_auto_finds_both(self):
        with patch("promptlint.llm.shutil.which", return_value="/usr/bin/mock"):
            assert resolve_backends(["auto"]) == ["claude", "codex"]

    def test_auto_finds_none(self):
        with patch("promptlint.llm.shutil.which", return_value=None):
            assert resolve_backends(["auto"]) == []

    def test_explicit_backends(self):
        assert resolve_backends(["claude", "codex"]) == ["claude", "codex"]

    def test_deduplication(self):
        assert resolve_backends(["claude", "claude"]) == ["claude"]

    def test_unknown_backend_ignored(self):
        assert resolve_backends(["claude", "unknown_thing"]) == ["claude"]

    def test_auto_plus_explicit_deduped(self):
        """auto expands, then explicit claude is deduped."""
        with patch("promptlint.llm.shutil.which", return_value="/usr/bin/mock"):
            assert resolve_backends(["auto", "claude"]) == ["claude", "codex"]
