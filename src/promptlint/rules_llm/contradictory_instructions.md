---
rule_id: contradictory_instructions
---

# contradictory_instructions — 指令之间矛盾

Detect pairs of instructions that contradict each other. Contradictions force the model to spend reasoning tokens reconciling conflicts instead of performing the actual task, degrading output quality.

## Examples

❌ "Always respond in JSON format." + "Write your answer as a natural paragraph."
❌ "Keep responses under 100 words." + "Provide comprehensive, detailed explanations."
❌ "Never use external tools." + "Search the web when you don't know the answer."
