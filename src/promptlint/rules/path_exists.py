"""Rule: all absolute file paths referenced in the prompt must exist."""

from __future__ import annotations

import re
from pathlib import Path

from promptlint.rules.base import BaseRule, RuleConfig, Violation

# Match absolute paths like /home/user/foo.py, /etc/nginx/conf.d/
# Require at least 3 segments to avoid matching lone /flags or /endpoints
_PATH_RE = re.compile(r"(\/[\w.+-]+(?:\/[\w.+-]+){2,})")
# Detect URLs in a line to skip their path components
_URL_RE = re.compile(r"https?://\S+")


class PathExistsRule(BaseRule):
    rule_id = "path_exists"
    description = "All referenced absolute file paths must exist"
    rule_type = "hardcoded"

    def check(self, content: str, file_path: Path) -> list[Violation]:
        violations: list[Violation] = []
        seen: set[str] = set()

        for i, line in enumerate(content.split("\n"), start=1):
            # Collect URL spans to skip paths inside URLs
            url_spans = [(u.start(), u.end()) for u in _URL_RE.finditer(line)]

            for m in _PATH_RE.finditer(line):
                # Skip if this match falls within a URL
                if any(us <= m.start() < ue for us, ue in url_spans):
                    continue
                path_str = m.group(1)
                if path_str in seen:
                    continue
                seen.add(path_str)

                try:
                    exists = Path(path_str).exists()
                except PermissionError:
                    exists = False  # can't access = treat as missing
                if not exists:
                    violations.append(Violation(
                        rule_id=self.rule_id,
                        message=f"Path does not exist: {path_str}",
                        severity=self.config.severity,
                        line=i,
                        snippet=line.strip()[:120],
                    ))

        return violations
