"""LLM-interpreted rules loaded from markdown files.

Each .md file in rules_llm/ defines one rule via YAML frontmatter + markdown body.
No Python subclass needed — the markdown IS the rule definition.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import yaml

from promptlint.llm import call_llm
from promptlint.rules_hardcode.base import BaseRule, RuleConfig, RuleContext, RuleType, Violation

logger = logging.getLogger(__name__)

LLM_RULES_DIR = Path(__file__).parent

_JUDGE_PROMPT_TEMPLATE = """\
You are a prompt quality linter. Your job is to check a prompt file against a specific rule.

## Rule: {rule_id}
{rule_description}

## Examples of violations:
{examples}

## Prompt to check:
<prompt file="{file_name}">
{content}
</prompt>

## Instructions:
Check if the prompt violates the rule above.
Respond with a JSON array of violations. Each violation is an object with:
- "message": brief description, under 50 chars (in Chinese)
- "snippet": the relevant text (up to 60 chars)
- "line": approximate line number (integer, or null)

If there are NO violations, respond with an empty array: []

IMPORTANT: Respond ONLY with the JSON array. Keep messages SHORT."""


def _parse_rule_md(md_path: Path) -> dict[str, str]:
    """Parse a rule .md file into {rule_id, description, examples}."""
    text = md_path.read_text(encoding="utf-8")

    # Split frontmatter from body
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"Rule file {md_path} missing YAML frontmatter")

    meta = yaml.safe_load(match.group(1))
    body = match.group(2).strip()

    rule_id = meta["rule_id"]

    # Split body into description (before ## Examples) and examples (after)
    parts = re.split(r"^## Examples?\s*$", body, maxsplit=1, flags=re.MULTILINE)
    # Strip the leading "# rule_id — ..." title line from description
    desc_text = parts[0].strip()
    desc_lines = desc_text.splitlines()
    if desc_lines and desc_lines[0].startswith("#"):
        desc_text = "\n".join(desc_lines[1:]).strip()

    examples = parts[1].strip() if len(parts) > 1 else ""

    return {"rule_id": rule_id, "description": desc_text, "examples": examples}


class LLMRule(BaseRule):
    """Rule that uses LLM to judge prompt quality. Loaded from .md files."""

    _skip_validation = True
    rule_type = RuleType.LLM_INTERPRET

    def __init__(self, config: RuleConfig | None = None, *, md_path: Path | None = None):
        super().__init__(config)
        self.model = self.config.params.get("model")
        self.backend = self.config.params.get("backend", "auto")

        if md_path is not None:
            parsed = _parse_rule_md(md_path)
            self.rule_id = parsed["rule_id"]
            self.description = parsed["description"]
            self.examples = parsed["examples"]
        else:
            self.examples = getattr(self, "examples", "")

    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        prompt = _JUDGE_PROMPT_TEMPLATE.format(
            rule_id=self.rule_id,
            rule_description=self.description,
            examples=self.examples,
            file_name=file_path.name,
            content=content[:8000],
        )

        resp = call_llm(prompt, backend=self.backend, model=self.model)
        if not resp.ok:
            logger.warning("LLM rule %s failed: %s", self.rule_id, resp.error)
            return []

        return self._parse_response(resp.text)

    def _parse_response(self, text: str) -> list[Violation]:
        """Parse LLM JSON response into Violation objects."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            # Strip opening fence line; strip closing fence if present
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            else:
                lines = lines[1:]
            text = "\n".join(lines)

        try:
            items = json.loads(text)
        except json.JSONDecodeError:
            for suffix in ("]", "}]", '"}]', '"}\n]'):
                try:
                    items = json.loads(text + suffix)
                    break
                except json.JSONDecodeError:
                    continue
            else:
                logger.warning("LLM rule %s: failed to parse JSON: %s", self.rule_id, text[:200])
                return []

        if not isinstance(items, list):
            return []

        violations = []
        for item in items:
            if not isinstance(item, dict):
                continue
            violations.append(Violation(
                rule_id=self.rule_id,
                message=item.get("message", "LLM-detected violation"),
                severity=self.config.severity,
                line=item.get("line"),
                snippet=item["snippet"][:120] if item.get("snippet") else None,
            ))
        return violations


def discover_llm_rules() -> dict[str, Path]:
    """Scan rules/llm/ directory for .md rule files. Returns {rule_id: md_path}."""
    if not LLM_RULES_DIR.is_dir():
        return {}
    rules = {}
    for md_file in sorted(LLM_RULES_DIR.glob("*.md")):
        try:
            parsed = _parse_rule_md(md_file)
            rules[parsed["rule_id"]] = md_file
        except Exception as e:
            logger.warning("Skipping %s: %s", md_file, e)
    return rules
