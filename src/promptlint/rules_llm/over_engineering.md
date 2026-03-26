---
rule_id: over_engineering
---

# over_engineering — 过度工程化

Detect prompts that add unrelated defensive instructions which distract from the core task. Only flag instructions that are clearly unrelated boilerplate — generic "good practice" bolted onto an unrelated task.

IMPORTANT: Do NOT flag instructions that are part of defining a workflow, process, or methodology. If the prompt's purpose IS to define a comprehensive process (e.g., a TDD workflow, a design review process, a deployment checklist), then detailed steps, quality gates, and thoroughness requirements are the core task, not over-engineering. Only flag when defensive instructions are irrelevant to the prompt's stated purpose.

Test: Is this instruction unrelated boilerplate, or does it serve the prompt's stated purpose?

## Examples

### Violations (❌)

❌ Task is "fix the login bug" but prompt also says "Before making any changes, always create a backup" and "Add docstrings to all functions"
❌ Task is "summarize this article" but prompt adds "Consider backwards compatibility" and "Create abstractions for reusable patterns"

### Acceptable (✅)

✅ A TDD skill prompt requiring "every new function has a test" — that IS the task
✅ A design review process requiring architecture docs and review loops — that IS the process
✅ "Add retry logic to the API call. Use exponential backoff with max 3 retries." — specific and relevant
✅ A deployment checklist requiring rollback plans — directly relevant to deployment
