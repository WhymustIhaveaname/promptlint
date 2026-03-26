---
rule_id: contradictory_instructions
---

# contradictory_instructions — 指令之间矛盾

Detect pairs of ACTUAL instructions that directly and unavoidably contradict each other. Only flag when following both instructions simultaneously is logically impossible.

IMPORTANT — Do NOT flag:
- Examples, demonstrations, or "bad practice" illustrations (text marked with ❌, "Bad:", "Don't do this:") — these are NOT real instructions, even if they contradict something else in the prompt
- Conditional/scoped rules that apply in different situations (e.g., "do X for case A" vs "do Y for case B")
- A general rule with explicit exceptions ("Never do X" + "except when Y" is not a contradiction)
- Instructions that appear contradictory on the surface but are resolved by context or scope

## Examples

### Violations (❌)

❌ "Always respond in JSON format." + "Write your answer as a natural paragraph." — impossible to satisfy both
❌ "Keep responses under 100 words." + "Provide comprehensive, detailed explanations." — directly opposing constraints on the same output

### Acceptable (✅)

✅ "❌ Bad: use @links" shown as example + later actually using @links — the ❌ is an example, not an instruction
✅ "Never do X" + "except with explicit user consent" — exception clause, not contradiction
✅ "Do X for case A" + "Do Y for case B" — scoped to different situations
✅ "Subagents work in parallel (safe)" + "Don't dispatch multiple agents on same files" — different scopes (safe tasks vs conflicting tasks)
