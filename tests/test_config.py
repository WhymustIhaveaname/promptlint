"""Tests for config loading."""

from pathlib import Path

from promptlint.config import load_config, parse_rule_config, DEFAULT_PATTERNS
from promptlint.rules.base import RuleConfig


def test_load_missing_config():
    """No config file -> returns defaults."""
    result = load_config(Path("/nonexistent/promptlint.yml"))
    assert result["rules"] == {}
    assert result["files"] == DEFAULT_PATTERNS


def test_load_valid_config(tmp_path):
    cfg = tmp_path / "promptlint.yml"
    cfg.write_text(
        "files:\n  - '*.md'\nrules:\n  max_lines:\n    severity: warn\n    max: 100\n"
    )
    result = load_config(cfg)
    assert result["files"] == ["*.md"]
    assert result["rules"]["max_lines"]["severity"] == "warn"
    assert result["rules"]["max_lines"]["max"] == 100


def test_load_empty_config(tmp_path):
    cfg = tmp_path / "promptlint.yml"
    cfg.write_text("")
    result = load_config(cfg)
    assert result["rules"] == {}
    assert result["files"] == DEFAULT_PATTERNS


def test_parse_rule_config_full():
    raw = {"enabled": False, "severity": "info", "max": 200, "extra": "val"}
    cfg = parse_rule_config("test", raw)
    assert cfg.enabled is False
    assert cfg.severity == "info"
    assert cfg.params == {"max": 200, "extra": "val"}


def test_parse_rule_config_defaults():
    cfg = parse_rule_config("test", {})
    assert cfg.enabled is True
    assert cfg.severity == "error"
    assert cfg.params == {}
