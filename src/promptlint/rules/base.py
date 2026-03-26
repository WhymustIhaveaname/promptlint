"""Base class for all promptlint rules.

Third-party plugins implement this interface and register via entry_points:

    [project.entry-points."promptlint.rules"]
    my_rule = "my_package.rules:MyRule"
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Violation:
    rule_id: str
    message: str
    severity: str = "error"  # error | warn | info
    line: int | None = None
    snippet: str | None = None


@dataclass
class RuleConfig:
    """Per-rule config from YAML. Extra keys go into `params`."""
    enabled: bool = True
    severity: str = "error"
    params: dict[str, Any] = field(default_factory=dict)


class BaseRule(abc.ABC):
    """All rules (hardcoded, llm-interpreted, llm-response) inherit from this."""

    # Subclass must set these
    rule_id: str = ""
    description: str = ""
    rule_type: str = "hardcoded"  # hardcoded | llm_interpret | llm_response

    def __init__(self, config: RuleConfig | None = None):
        self.config = config or RuleConfig()

    @abc.abstractmethod
    def check(self, content: str, file_path: Path) -> list[Violation]:
        """Run this rule against file content. Return list of violations."""
        ...
