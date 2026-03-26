"""Rule engine: discovers rules via entry_points, runs them against files."""

from __future__ import annotations

import logging
from importlib.metadata import entry_points
from pathlib import Path

from promptlint.config import load_config, parse_rule_config
from promptlint.rules.base import BaseRule, RuleConfig, RuleContext, Violation

logger = logging.getLogger(__name__)


def discover_rules() -> dict[str, type[BaseRule]]:
    """Find all registered rules via entry_points."""
    rules: dict[str, type[BaseRule]] = {}
    eps = entry_points(group="promptlint.rules")
    for ep in eps:
        cls = ep.load()
        rules[ep.name] = cls
    return rules


def resolve_files(patterns: list[str], scan_path: Path) -> list[Path]:
    """Glob for prompt files matching patterns."""
    files: set[Path] = set()
    for pattern in patterns:
        files.update(scan_path.glob(pattern))
    return sorted(files)


def run(
    scan_path: Path,
    config_path: Path | None = None,
    files: list[Path] | None = None,
) -> dict[Path, list[Violation]]:
    """Main entry: load config, discover rules, run against files."""
    config = load_config(config_path)
    rule_classes = discover_rules()
    configured_rules = config["rules"]

    # Only run rules that are explicitly listed in config.
    # Third-party plugins discovered via entry_points but not in config are skipped.
    active_rules: list[BaseRule] = []
    for rule_name, rule_cls in rule_classes.items():
        if rule_name not in configured_rules:
            continue
        rule_cfg = parse_rule_config(rule_name, configured_rules[rule_name])
        if not rule_cfg.enabled:
            continue
        active_rules.append(rule_cls(rule_cfg))

    # Resolve files to scan
    if files is None:
        files = resolve_files(config["files"], scan_path)

    ctx = RuleContext(scan_path=scan_path)

    # Run
    results: dict[Path, list[Violation]] = {}
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("Skipping %s: %s", file_path, e)
            continue

        file_violations: list[Violation] = []
        for rule in active_rules:
            file_violations.extend(rule.check(content, file_path, ctx))
        if file_violations:
            results[file_path] = file_violations

    return results
