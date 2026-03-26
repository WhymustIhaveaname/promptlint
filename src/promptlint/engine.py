"""Rule engine: discovers rules via entry_points, runs them against files."""

from __future__ import annotations

import sys
from importlib.metadata import entry_points
from pathlib import Path

from promptlint.config import load_config, parse_rule_config
from promptlint.rules.base import BaseRule, RuleConfig, Violation


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

    # Instantiate rules with config
    active_rules: list[BaseRule] = []
    for rule_name, rule_cls in rule_classes.items():
        rule_cfg_raw = config["rules"].get(rule_name, {})
        rule_cfg = parse_rule_config(rule_name, rule_cfg_raw) if rule_cfg_raw else RuleConfig()
        if not rule_cfg.enabled:
            continue
        active_rules.append(rule_cls(rule_cfg))

    # Resolve files to scan
    if files is None:
        files = resolve_files(config["files"], scan_path)

    # Run
    results: dict[Path, list[Violation]] = {}
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        file_violations: list[Violation] = []
        for rule in active_rules:
            file_violations.extend(rule.check(content, file_path))
        if file_violations:
            results[file_path] = file_violations

    return results
