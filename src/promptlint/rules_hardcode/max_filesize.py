"""Rule: prompt file must not exceed a maximum size in bytes."""

from __future__ import annotations

from pathlib import Path

from promptlint.rules_hardcode.base import BaseRule, RuleConfig, RuleContext, Violation


class MaxFilesizeRule(BaseRule):
    rule_id = "max_filesize"
    description = "Prompt file must not exceed maximum file size"

    def __init__(self, config: RuleConfig | None = None):
        super().__init__(config)
        self.max_bytes = self.config.params.get("max_bytes", 10240)  # 10 KB

    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        size = len(content.encode("utf-8"))
        if size > self.max_bytes:
            size_kb = size / 1024
            max_kb = self.max_bytes / 1024
            return [Violation(
                rule_id=self.rule_id,
                message=f"File is {size_kb:.1f} KB, exceeds max {max_kb:.1f} KB",
                severity=self.config.severity,
            )]
        return []
