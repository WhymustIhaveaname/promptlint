---
rule_id: over_engineering
---

# over_engineering — 过度工程化

Detect prompts stuffed with defensive 'just in case' instructions that are not directly relevant to the task. These distract the model and cause overly cautious, bloated output. Instructions like 'always create backups', 'add comprehensive error handling', 'add type annotations to all functions' are over-engineering if the task is simply 'fix a bug'.

Test: is this instruction directly relevant to the specific task, or is it generic 'good practice'?

## Examples

❌ Task is "fix the login bug" but prompt also says:
   - "Before making any changes, always create a backup"
   - "Add comprehensive error handling for all edge cases"
   - "Add type annotations to all functions"
   - "Add docstrings to all functions"
   - "Consider backwards compatibility"
   - "Create abstractions for reusable patterns"
✅ "Fix the bug in the login function." (focused on the task)
