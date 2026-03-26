"""Rule: prompt file must not exceed a maximum number of lines."""

from __future__ import annotations

from pathlib import Path

from promptlint.rules.base import BaseRule, RuleConfig, Violation


class MaxLinesRule(BaseRule):
    rule_id = "max_lines"
    description = "Prompt file must not exceed maximum line count"
    rule_type = "hardcoded"

    def __init__(self, config: RuleConfig | None = None):
        super().__init__(config)
        self.max = self.config.params.get("max", 500)

    def check(self, content: str, file_path: Path) -> list[Violation]:
        lines = content.split("\n")
        count = len(lines)
        if count > self.max:
            return [Violation(
                rule_id=self.rule_id,
                message=f"File has {count} lines, exceeds max {self.max}",
                severity=self.config.severity,
            )]
        return []
