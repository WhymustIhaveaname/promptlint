"""Load promptlint YAML config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from promptlint.rules_hardcode.base import RuleConfig

DEFAULT_CONFIG_NAME = "promptlint.yml"

# Default file patterns to scan (like promptfoo)
DEFAULT_PATTERNS = [
    "**/*.prompt",
    "**/*.prompt.txt",
    "**/*.prompt.md",
    "**/SKILL.md",
    "**/*-SKILL.md",
    "**/*_SKILL.md",
]


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load config from YAML. Returns parsed dict with 'rules' key."""
    if path is None:
        path = Path(DEFAULT_CONFIG_NAME)
    if not path.exists():
        return {"rules": {}, "files": DEFAULT_PATTERNS}

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    return {
        "rules": raw.get("rules", {}),
        "files": raw.get("files", DEFAULT_PATTERNS),
    }


def parse_rule_config(rule_id: str, raw: dict[str, Any]) -> RuleConfig:
    """Parse per-rule config from the 'rules' section."""
    return RuleConfig(
        enabled=raw.get("enabled", True),
        severity=raw.get("severity", "error"),
        params={k: v for k, v in raw.items() if k not in ("enabled", "severity")},
    )
