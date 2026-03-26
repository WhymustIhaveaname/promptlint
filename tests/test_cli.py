"""Tests for CLI commands."""

from pathlib import Path

from click.testing import CliRunner

from promptlint.cli import main


class TestInit:
    def test_creates_config(self, tmp_path):
        runner = CliRunner()
        out = tmp_path / "promptlint.yml"
        result = runner.invoke(main, ["init", "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        assert "Created" in result.output

    def test_refuses_overwrite_without_force(self, tmp_path):
        out = tmp_path / "promptlint.yml"
        out.write_text("existing")
        runner = CliRunner()
        result = runner.invoke(main, ["init", "-o", str(out)])
        assert "already exists" in result.output
        assert out.read_text() == "existing"

    def test_force_overwrites(self, tmp_path):
        out = tmp_path / "promptlint.yml"
        out.write_text("existing")
        runner = CliRunner()
        result = runner.invoke(main, ["init", "-o", str(out), "--force"])
        assert result.exit_code == 0
        assert out.read_text() != "existing"


class TestScan:
    def test_all_checks_passed(self, tmp_path):
        prompt = tmp_path / "test-SKILL.md"
        prompt.write_text("short file")
        cfg = tmp_path / "promptlint.yml"
        cfg.write_text(
            "files:\n  - '**/*-SKILL.md'\n"
            "rules:\n  max_lines:\n    severity: error\n    max: 100\n"
        )
        runner = CliRunner()
        result = runner.invoke(main, ["scan", str(tmp_path), "-c", str(cfg)])
        assert result.exit_code == 0
        assert "All checks passed" in result.output

    def test_error_violation_exit_code_1(self, tmp_path):
        prompt = tmp_path / "test-SKILL.md"
        prompt.write_text("\n".join(f"line{i}" for i in range(20)))
        cfg = tmp_path / "promptlint.yml"
        cfg.write_text(
            "files:\n  - '**/*-SKILL.md'\n"
            "rules:\n  max_lines:\n    severity: error\n    max: 10\n"
        )
        runner = CliRunner()
        result = runner.invoke(main, ["scan", str(tmp_path), "-c", str(cfg)])
        assert result.exit_code == 1
        assert "violation(s) found" in result.output

    def test_warn_violation_exit_code_0(self, tmp_path):
        prompt = tmp_path / "test-SKILL.md"
        prompt.write_text("\n".join(f"line{i}" for i in range(20)))
        cfg = tmp_path / "promptlint.yml"
        cfg.write_text(
            "files:\n  - '**/*-SKILL.md'\n"
            "rules:\n  max_lines:\n    severity: warn\n    max: 10\n"
        )
        runner = CliRunner()
        result = runner.invoke(main, ["scan", str(tmp_path), "-c", str(cfg)])
        assert result.exit_code == 0
        assert "violation(s) found" in result.output
