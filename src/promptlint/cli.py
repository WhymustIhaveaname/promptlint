"""CLI entry point for promptlint."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from promptlint.engine import run
from promptlint.rules.base import Violation


def _severity_icon(severity: str) -> str:
    return {"error": "\u2716", "warn": "\u26a0", "info": "\u2139"}.get(severity, "?")


def _print_results(results: dict[Path, list[Violation]], base: Path) -> int:
    """Print results, return exit code (1 if any error-level violations)."""
    has_error = False
    total = 0

    for file_path, violations in sorted(results.items()):
        rel = file_path.relative_to(base) if file_path.is_relative_to(base) else file_path
        click.echo(f"\n{rel}")
        for v in violations:
            icon = _severity_icon(v.severity)
            loc = f"L{v.line}" if v.line else ""
            click.echo(f"  {icon} [{v.severity}] {v.rule_id}: {v.message} {loc}")
            if v.snippet:
                click.echo(f"    > {v.snippet[:120]}")
            total += 1
            if v.severity == "error":
                has_error = True

    if total == 0:
        click.echo("All checks passed.")
    else:
        click.echo(f"\n{total} violation(s) found.")

    return 1 if has_error else 0


@click.group()
def main():
    """promptlint - Lint and test LLM prompts."""
    pass


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--config", "-c", "config_path", default=None, help="Config file path")
def scan(path: str, config_path: str | None):
    """Scan prompt files for violations."""
    scan_path = Path(path).resolve()
    cfg = Path(config_path) if config_path else None
    results = run(scan_path, cfg)
    code = _print_results(results, scan_path)
    sys.exit(code)


@main.command()
@click.option("--output", "-o", default="promptlint.yml", help="Output path")
@click.option("--force", is_flag=True, help="Overwrite existing config file")
def init(output: str, force: bool):
    """Create a starter config file."""
    out = Path(output)
    if out.exists() and not force:
        click.echo(f"{out} already exists. Use --force to overwrite.")
        return

    out.write_text(
        """\
# promptlint config
# Docs: https://github.com/youcommit/promptlint

files:
  - "**/*.prompt"
  - "**/*.prompt.md"
  - "**/SKILL.md"
  - "**/*-SKILL.md"

rules:
  max_lines:
    severity: error
    max: 500

  path_exists:
    severity: warn
""",
        encoding="utf-8",
    )
    click.echo(f"Created {out}")
