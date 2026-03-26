"""LLM backend: calls claude or codex CLI for LLM-interpreted rules."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_TIMEOUT = 120


@dataclass
class LLMResponse:
    text: str
    ok: bool
    error: str | None = None


def _run_cli(cmd: list[str], cli_name: str) -> subprocess.CompletedProcess[str] | LLMResponse:
    """Run a CLI command, returning CompletedProcess on success or LLMResponse on error."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=_TIMEOUT)
    except FileNotFoundError:
        return LLMResponse(text="", ok=False, error=f"{cli_name} CLI not found")
    except subprocess.TimeoutExpired:
        return LLMResponse(text="", ok=False, error=f"{cli_name} CLI timed out ({_TIMEOUT}s)")

    if result.returncode != 0:
        return LLMResponse(text="", ok=False, error=f"{cli_name} CLI error: {result.stderr[:500]}")

    return result


def call_claude(prompt: str, model: str = "sonnet") -> LLMResponse:
    """Call claude CLI in non-interactive mode (-p)."""
    result = _run_cli(
        ["claude", "-p", prompt, "--model", model, "--output-format", "json"],
        "claude",
    )
    if isinstance(result, LLMResponse):
        return result

    try:
        data = json.loads(result.stdout)
        return LLMResponse(text=data.get("result", ""), ok=True)
    except (json.JSONDecodeError, KeyError):
        return LLMResponse(text=result.stdout.strip(), ok=True)


def call_codex(prompt: str, model: str = "gpt-5.4") -> LLMResponse:
    """Call codex CLI in non-interactive exec mode (--json)."""
    result = _run_cli(["codex", "exec", prompt, "--json"], "codex")
    if isinstance(result, LLMResponse):
        return result

    # Parse JSONL output, find last item.completed message
    text = ""
    for line in result.stdout.strip().splitlines():
        try:
            event = json.loads(line)
            if event.get("type") == "item.completed":
                text = event.get("item", {}).get("text", "")
        except json.JSONDecodeError:
            continue

    if not text:
        return LLMResponse(text="", ok=False, error="codex returned no text")

    return LLMResponse(text=text, ok=True)


def call_llm(prompt: str, backend: str = "auto", model: str | None = None) -> LLMResponse:
    """Unified LLM call. Backend: 'claude', 'codex', or 'auto' (try claude first)."""
    if backend == "auto":
        if shutil.which("claude"):
            backend = "claude"
        elif shutil.which("codex"):
            backend = "codex"
        else:
            return LLMResponse(text="", ok=False, error="No LLM CLI found (tried claude, codex)")

    if backend == "claude":
        return call_claude(prompt, model=model or "sonnet")
    if backend == "codex":
        return call_codex(prompt, model=model or "gpt-5.4")
    return LLMResponse(text="", ok=False, error=f"Unknown backend: {backend}")
