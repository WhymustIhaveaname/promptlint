"""Base class for all promptlint rules.

Third-party plugins implement this interface and register via entry_points:

    [project.entry-points."promptlint.rules"]
    my_rule = "my_package.rules:MyRule"
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RuleType(Enum):
    HARDCODED = "hardcoded"
    LLM_INTERPRET = "llm_interpret"
    LLM_RESPONSE = "llm_response"


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


@dataclass
class RuleContext:
    """Extra context passed to rules during check.

    Hardcoded rules can ignore this. LLM rules will use `llm_client` etc.
    """
    scan_path: Path | None = None
    # Future: llm_client, environment, user metadata, etc.


class BaseRule(abc.ABC):
    """All rules (hardcoded, llm-interpreted, llm-response) inherit from this."""

    # Subclass must set these
    rule_id: str = ""
    description: str = ""
    rule_type: RuleType = RuleType.HARDCODED

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, '__abstractmethods__', None):
            # Only validate concrete (non-abstract) subclasses
            if not cls.rule_id:
                raise TypeError(f"{cls.__name__} must set a non-empty 'rule_id'")
            if not cls.description:
                raise TypeError(f"{cls.__name__} must set a non-empty 'description'")

    def __init__(self, config: RuleConfig | None = None):
        self.config = config or RuleConfig()

    @abc.abstractmethod
    def check(self, content: str, file_path: Path, ctx: RuleContext | None = None) -> list[Violation]:
        """Run this rule against file content. Return list of violations."""
        ...
