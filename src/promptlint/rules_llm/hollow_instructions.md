---
rule_id: hollow_instructions
---

# hollow_instructions — 空洞指令

Detect standalone, top-level instructions that are pure platitudes — they describe default LLM behavior and removing them would change nothing. Only flag the most egregious cases: generic adjective-stacking with zero specificity.

Core test: for every line in the prompt, ask yourself: **"Would removing it cause the model to make mistakes?"** If not, it's noise — flag it.

Do NOT flag:
- Instructions that reinforce a point within a larger workflow or checklist context
- Instructions that, while brief, are paired with specific details nearby
- Motivational framing that sets tone for a creative or collaborative task

Only flag when the instruction is a standalone platitude that adds zero information.

## Examples

### Violations (❌)

❌ "Be helpful and accurate" — pure default behavior
❌ "Provide high-quality answers" — means nothing specific
❌ "Think carefully before responding" — the model already does this

### Acceptable (✅)

✅ "Use snake_case for variables, camelCase for functions" — specific constraint
✅ "Keep functions under 20 lines" — measurable limit
✅ "Be creative but grounded in existing research" within a brainstorming prompt — sets tone for the task
✅ "Stay focused on what serves the current goal" in a multi-step workflow — a reminder with contextual value
