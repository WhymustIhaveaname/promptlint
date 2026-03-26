"""Rule: all XML tags in the prompt must be properly closed."""

from __future__ import annotations

import re
from pathlib import Path

from promptlint.rules.base import BaseRule, RuleConfig, RuleContext, Violation

# Match XML-style tags: <tag_name> or <tag_name attr="val">
# Only match tags without spaces in the tag name (to skip placeholders like <arXiv ID>)
_OPEN_TAG_RE = re.compile(r"<([a-zA-Z][\w_-]*)(\s+[a-zA-Z][\w_-]*\s*=\s*[\"'][^\"']*[\"'])*\s*>")
_CLOSE_TAG_RE = re.compile(r"</([a-zA-Z][\w_-]*)\s*>")
_SELF_CLOSING_RE = re.compile(r"<[a-zA-Z][\w_-]*(?:\s[^>]*)?\s*/>")
_CODE_FENCE_RE = re.compile(r"^```")


class UnclosedXmlTagsRule(BaseRule):
    rule_id = "unclosed_xml_tags"
    description = "All XML tags must be properly closed"

    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        open_tags: list[tuple[str, int]] = []
        close_tags: list[tuple[str, int]] = []

        in_code_block = False
        for i, line in enumerate(content.splitlines(), start=1):
            # Toggle code block state
            if _CODE_FENCE_RE.match(line.strip()):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Strip inline code (`...`) to avoid matching placeholders like `<ID>`
            cleaned = re.sub(r"`[^`]+`", "", line)
            cleaned = _SELF_CLOSING_RE.sub("", cleaned)
            for m in _OPEN_TAG_RE.finditer(cleaned):
                tag = m.group(1)
                # Skip ALL-CAPS tags (likely placeholders like <ID>, <URL>)
                if tag.isupper():
                    continue
                open_tags.append((tag.lower(), i))
            for m in _CLOSE_TAG_RE.finditer(cleaned):
                close_tags.append((m.group(1).lower(), i))

        # Count-based matching
        close_count: dict[str, int] = {}
        for tag, _ in close_tags:
            close_count[tag] = close_count.get(tag, 0) + 1

        violations: list[Violation] = []
        for tag, line in open_tags:
            if close_count.get(tag, 0) > 0:
                close_count[tag] -= 1
            else:
                violations.append(Violation(
                    rule_id=self.rule_id,
                    message=f"Tag <{tag}> opened but never closed",
                    severity=self.config.severity,
                    line=line,
                ))

        return violations
