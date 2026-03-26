---
rule_id: contradictory_instructions
---

# contradictory_instructions — 指令之间矛盾

Detect pairs of instructions that contradict each other. Contradictions force the model to spend reasoning tokens reconciling conflicts instead of performing the actual task, degrading output quality.

## Examples

### Violations (❌)

❌ "Always respond in JSON format." + "Write your answer as a natural paragraph."
❌ "Keep responses under 100 words." + "Provide comprehensive, detailed explanations."
❌ "Never use external tools." + "Search the web when you don't know the answer."

### Acceptable (✅)

✅ "Respond in JSON format." — 单一格式要求，无矛盾
✅ "Keep responses concise, targeting 2-3 sentences per point." — 有明确范围，不与"详细"矛盾
✅ "Use web search for factual questions. Use internal knowledge for opinions." — 按场景分工，不矛盾
