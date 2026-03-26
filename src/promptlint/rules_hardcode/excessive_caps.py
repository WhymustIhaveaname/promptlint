"""Rule: ALL-CAPS emphasis words should not be overused."""

from __future__ import annotations

import re
from pathlib import Path

from promptlint.rules_hardcode.base import BaseRule, RuleConfig, RuleContext, Violation

# Common emphasis words that are often ALL-CAPS in prompts
_CAPS_WORDS = {
    "MUST", "ALWAYS", "NEVER", "CRITICAL", "IMPORTANT",
    "REQUIRED", "MANDATORY", "ABSOLUTELY", "ESSENTIAL",
    "CRUCIAL", "VITAL", "WARNING", "FORBIDDEN", "PROHIBITED",
    "EXACTLY", "STRICTLY", "URGENT",
}

_WORD_RE = re.compile(r"\b[A-Z]{2,}\b")


class ExcessiveCapsRule(BaseRule):
    rule_id = "excessive_caps"
    description = "ALL-CAPS emphasis words should not be overused"

    def __init__(self, config: RuleConfig | None = None):
        super().__init__(config)
        self.max_density = self.config.params.get("max_density", 0.03)  # 3% of words

    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        words = content.split()
        if len(words) < 20:
            return []

        caps_matches = []
        for i, line in enumerate(content.splitlines(), start=1):
            for m in _WORD_RE.finditer(line):
                word = m.group()
                if word in _CAPS_WORDS:
                    caps_matches.append((word, i, line.strip()))

        density = len(caps_matches) / len(words)
        if density <= self.max_density:
            return []

        violations = [Violation(
            rule_id=self.rule_id,
            message=f"ALL-CAPS emphasis density too high: {len(caps_matches)} caps words in {len(words)} words ({density:.1%}). Max allowed: {self.max_density:.0%}",
            severity=self.config.severity,
        )]

        # Also report each occurrence
        for word, line, snippet in caps_matches:
            violations.append(Violation(
                rule_id=self.rule_id,
                message=f"ALL-CAPS: {word}",
                severity="info",
                line=line,
                snippet=snippet[:120],
            ))

        return violations
