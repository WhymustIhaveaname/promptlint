"""Base class for LLM-interpreted rules.

Sends rule description + prompt content to LLM, asks it to judge violations.
Similar to korchasa/promptlint approach.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from promptlint.llm import call_llm
from promptlint.rules.base import BaseRule, RuleConfig, RuleContext, RuleType, Violation

logger = logging.getLogger(__name__)

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


class LLMRule(BaseRule):
    """Base for rules that use LLM to judge prompt quality."""

    _skip_validation = True  # intermediate base, not a concrete rule
    rule_type = RuleType.LLM_INTERPRET

    # Subclasses must set these
    examples: str = ""

    def __init__(self, config: RuleConfig | None = None):
        super().__init__(config)
        self.model = self.config.params.get("model")
        self.backend = self.config.params.get("backend", "auto")

    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        prompt = _JUDGE_PROMPT_TEMPLATE.format(
            rule_id=self.rule_id,
            rule_description=self.description,
            examples=self.examples,
            file_name=file_path.name,
            content=content[:8000],  # cap to avoid huge prompts
        )

        resp = call_llm(prompt, backend=self.backend, model=self.model)
        if not resp.ok:
            logger.warning("LLM rule %s failed: %s", self.rule_id, resp.error)
            return []

        return self._parse_response(resp.text)

    def _parse_response(self, text: str) -> list[Violation]:
        """Parse LLM JSON response into Violation objects."""
        # Extract JSON array from response (LLM might wrap it in markdown)
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            items = json.loads(text)
        except json.JSONDecodeError:
            # Try to salvage truncated JSON by closing brackets
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
                snippet=item.get("snippet", "")[:120] if item.get("snippet") else None,
            ))
        return violations
