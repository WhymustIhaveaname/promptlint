"""Integration tests for the rule engine."""

import json
from pathlib import Path
from unittest.mock import patch

from promptlint.engine import run, discover_rules, resolve_files
from promptlint.llm import LLMResponse


def test_discover_rules_finds_builtins():
    rules = discover_rules()
    assert "max_lines" in rules
    assert "path_exists" in rules


def test_resolve_files(tmp_path):
    (tmp_path / "a.prompt").touch()
    (tmp_path / "b.txt").touch()
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "SKILL.md").touch()

    files = resolve_files(["**/*.prompt", "**/SKILL.md"], tmp_path)
    names = [f.name for f in files]
    assert "a.prompt" in names
    assert "SKILL.md" in names
    assert "b.txt" not in names


def test_run_with_config(tmp_path):
    # Create a prompt file that's too long
    prompt = tmp_path / "test-SKILL.md"
    prompt.write_text("\n".join(f"line{i}" for i in range(15)))

    cfg = tmp_path / "promptlint.yml"
    cfg.write_text(
        "files:\n  - '**/*-SKILL.md'\nrules:\n  max_lines:\n    severity: error\n    max: 10\n"
    )

    results = run(tmp_path, cfg)
    assert prompt in results
    assert results[prompt][0].rule_id == "max_lines"


def test_run_unconfigured_rules_skipped(tmp_path):
    """Rules not in config should NOT run (even if discovered via entry_points)."""
    prompt = tmp_path / "test-SKILL.md"
    prompt.write_text("short file")

    # Config only enables max_lines, not path_exists
    cfg = tmp_path / "promptlint.yml"
    cfg.write_text(
        "files:\n  - '**/*-SKILL.md'\nrules:\n  max_lines:\n    severity: error\n    max: 500\n"
    )

    results = run(tmp_path, cfg)
    # Even if file contains non-existent paths, path_exists should not run
    assert results == {}


def test_run_no_config(tmp_path, monkeypatch):
    """Without a config file, no rules should run (nothing configured)."""
    monkeypatch.chdir(tmp_path)  # ensure no promptlint.yml in CWD
    prompt = tmp_path / "SKILL.md"
    prompt.write_text("/nonexistent/deep/path/file.py\n" * 600)

    results = run(tmp_path)
    assert results == {}


def test_run_skips_unreadable_file(tmp_path):
    prompt = tmp_path / "test-SKILL.md"
    prompt.write_bytes(b"\x80\x81\x82\xff" * 100)  # invalid UTF-8

    cfg = tmp_path / "promptlint.yml"
    cfg.write_text(
        "files:\n  - '**/*-SKILL.md'\nrules:\n  max_lines:\n    severity: error\n    max: 10\n"
    )

    # Should not raise, just skip the file
    results = run(tmp_path, cfg)
    assert results == {}


def test_run_disabled_rule_skipped(tmp_path):
    """A rule with enabled: false in config should not run."""
    prompt = tmp_path / "test-SKILL.md"
    prompt.write_text("\n".join(f"line{i}" for i in range(200)))

    cfg = tmp_path / "promptlint.yml"
    cfg.write_text(
        "files:\n  - '**/*-SKILL.md'\n"
        "rules:\n  max_lines:\n    enabled: false\n    max: 10\n"
    )

    results = run(tmp_path, cfg)
    assert results == {}


def test_run_llm_rule_integration(tmp_path):
    """LLM rules from .md files should be discovered and run by the engine."""
    prompt = tmp_path / "test-SKILL.md"
    prompt.write_text("Be helpful and accurate.")

    cfg = tmp_path / "promptlint.yml"
    cfg.write_text(
        "files:\n  - '**/*-SKILL.md'\n"
        "rules:\n  hollow_instructions:\n    severity: warn\n"
    )

    fake_response = json.dumps([{"message": "空洞指令", "snippet": "Be helpful", "line": 1}])
    with patch("promptlint.rules_llm.llm_base.call_llm",
               return_value=LLMResponse(text=fake_response, ok=True)):
        results = run(tmp_path, cfg)

    assert prompt in results
    assert results[prompt][0].rule_id == "hollow_instructions"
    assert results[prompt][0].severity == "warn"
