"""Rule engine: discovers rules via entry_points + rules_llm/*.md, runs them against files."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.metadata import entry_points
from pathlib import Path

from promptlint.config import load_config, parse_rule_config
from promptlint.rules_hardcode.base import BaseRule, RuleContext, Violation
from promptlint.rules_llm.llm_base import LLMRule, discover_llm_rules

logger = logging.getLogger(__name__)


def discover_rules() -> dict[str, type[BaseRule]]:
    """Find all registered hardcoded rules via entry_points."""
    return {ep.name: ep.load() for ep in entry_points(group="promptlint.rules")}


def resolve_files(patterns: list[str], scan_path: Path) -> list[Path]:
    """Glob for prompt files matching patterns."""
    files: set[Path] = set()
    for pattern in patterns:
        files.update(scan_path.glob(pattern))
    return sorted(files)


def _run_llm_rules_parallel(
    llm_rules: list[LLMRule],
    content: str,
    file_path: Path,
) -> list[Violation]:
    """Run all LLM (rule × backend) combinations in one thread pool."""
    # Build flat task list: [(rule, backend), ...]
    tasks: list[tuple[LLMRule, str]] = []
    for rule in llm_rules:
        for backend in rule.backends:
            tasks.append((rule, backend))

    if not tasks:
        return []

    # Single task — no need for a thread pool
    if len(tasks) == 1:
        rule, backend = tasks[0]
        return rule.check_single_backend(content, file_path, backend)

    violations: list[Violation] = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {
            executor.submit(rule.check_single_backend, content, file_path, backend): (rule, backend)
            for rule, backend in tasks
        }
        for future in as_completed(futures):
            rule, backend = futures[future]
            try:
                violations.extend(future.result())
            except Exception as e:
                logger.warning("LLM rule %s [%s] raised: %s", rule.rule_id, backend, e)

    return violations


def run(
    scan_path: Path,
    config_path: Path | None = None,
    files: list[Path] | None = None,
) -> dict[Path, list[Violation]]:
    """Main entry: load config, discover rules, run against files."""
    config = load_config(config_path)
    configured_rules = config["rules"]
    llm_config = config["llm"]

    # Collect enabled hardcoded + LLM rules
    rule_classes = discover_rules()
    llm_rule_paths = discover_llm_rules()

    hardcoded_rules: list[BaseRule] = []
    llm_rules: list[LLMRule] = []
    for rule_id, raw_cfg in configured_rules.items():
        rule_cfg = parse_rule_config(rule_id, raw_cfg)
        if not rule_cfg.enabled:
            continue
        if rule_id in rule_classes:
            hardcoded_rules.append(rule_classes[rule_id](rule_cfg))
        elif rule_id in llm_rule_paths:
            llm_rules.append(LLMRule(rule_cfg, md_path=llm_rule_paths[rule_id], llm_config=llm_config))

    # Resolve files to scan
    if files is None:
        files = resolve_files(config["files"], scan_path)

    ctx = RuleContext(scan_path=scan_path)

    results: dict[Path, list[Violation]] = {}
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("Skipping %s: %s", file_path, e)
            continue

        file_violations: list[Violation] = []

        # Hardcoded rules: fast, run serially
        for rule in hardcoded_rules:
            file_violations.extend(rule.check(content, file_path, ctx))

        # LLM rules: all (rule × backend) pairs in one thread pool
        file_violations.extend(_run_llm_rules_parallel(llm_rules, content, file_path))

        if file_violations:
            results[file_path] = file_violations

    return results
