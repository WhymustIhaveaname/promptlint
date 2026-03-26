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

from promptlint.config import LLMConfig
from promptlint.llm import call_llm, resolve_backends
from promptlint.rules_hardcode.base import BaseRule, RuleConfig, RuleContext, RuleType, Violation

logger = logging.getLogger(__name__)

LLM_RULES_DIR = Path(__file__).parent

_JUDGE_PROMPT_TEMPLATE = """\
<role>
You are an expert in LLM prompt engineering. Your task is to lint a prompt file against the rule defined below.
</role>

<rule>
{rule_md}
</rule>

<prompt file="{file_name}">
{content}
</prompt>

<output_format>
Respond with a JSON array. Each element is a violation object. If no violations, return `[]`.

Pass example:
[]

Fail example:
[{{"message": "使用了模糊动词", "snippet": "handle edge cases", "line": 5}}]

Fields:
- "message": brief description in Chinese, under 50 chars
- "snippet": the offending text, up to 60 chars
- "line": approximate line number (integer or null)

Only report clear violations. Respond ONLY with the JSON array.
</output_format>"""


def _parse_rule_md(md_path: Path) -> dict[str, str]:
    """Parse a rule .md file. Returns {rule_id, rule_md (raw body)}."""
    text = md_path.read_text(encoding="utf-8")

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"Rule file {md_path} missing YAML frontmatter")

    meta = yaml.safe_load(match.group(1))
    body = match.group(2).strip()

    return {"rule_id": meta["rule_id"], "rule_md": body}


class LLMRule(BaseRule):
    """Rule that uses LLM to judge prompt quality. Loaded from .md files."""

    _skip_validation = True
    rule_type = RuleType.LLM_INTERPRET

    def __init__(
        self,
        config: RuleConfig | None = None,
        *,
        md_path: Path | None = None,
        llm_config: LLMConfig | None = None,
    ):
        super().__init__(config)
        llm_config = llm_config or LLMConfig()

        # Rule-level 'backends' override global; fall back to global llm config
        rule_backends = self.config.params.get("backends")
        if rule_backends:
            self.backends = resolve_backends(rule_backends)
        else:
            self.backends = resolve_backends(llm_config.backends)

        # Merge models: global defaults, rule-level overrides on top
        self.models: dict[str, str] = {**llm_config.models}
        rule_model = self.config.params.get("model")
        if rule_model:
            # Single model applies to all backends for this rule
            for b in self.backends:
                self.models[b] = rule_model

        if md_path is not None:
            parsed = _parse_rule_md(md_path)
            self.rule_id = parsed["rule_id"]
            self.rule_md = parsed["rule_md"]
        else:
            self.rule_md = getattr(self, "rule_md", "")

    def build_prompt(self, content: str, file_path: Path) -> str:
        """Build the judge prompt for this rule. Used by engine for parallel dispatch."""
        return _JUDGE_PROMPT_TEMPLATE.format(
            rule_md=self.rule_md,
            file_name=file_path.name,
            content=content[:8000],
        )

    def check_single_backend(self, content: str, file_path: Path, backend: str) -> list[Violation]:
        """Run this rule against one backend. Returns violations tagged with source."""
        prompt = self.build_prompt(content, file_path)
        model = self.models.get(backend)
        resp = call_llm(prompt, backend=backend, model=model)
        if not resp.ok:
            logger.warning("LLM rule %s [%s] failed: %s", self.rule_id, backend, resp.error)
            return []
        violations = self._parse_response(resp.text)
        for v in violations:
            v.source = backend
        return violations

    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        """Run this rule against all backends sequentially. For parallel use, see engine."""
        all_violations: list[Violation] = []
        for backend in self.backends:
            all_violations.extend(self.check_single_backend(content, file_path, backend))
        return all_violations

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
