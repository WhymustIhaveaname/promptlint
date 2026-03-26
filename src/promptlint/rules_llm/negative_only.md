---
rule_id: negative_only
---

# negative_only — 只有否定没有正向替代

Detect imperative instructions that prohibit a behavior without giving the model any positive alternative to follow instead. The model needs to know what to do, not just what to avoid.

Only flag when:
- The instruction is a direct command to the model (e.g., "Don't do X", "Never do Y")
- There is no positive alternative anywhere nearby in the prompt

Do NOT flag:
- Lists of situations/conditions where something should NOT be used (e.g., "Don't parallelize when: shared state, debugging") — these are decision criteria, not behavior prohibitions
- Negative instructions that are immediately followed by a positive alternative in the same paragraph or list
- Constraints in examples or quoted text

## Examples

❌ "Do not use markdown formatting" (alone, no alternative) → should say "Write as prose paragraphs"
❌ "Don't make up information" (alone) → should say "Only answer based on provided documents"
✅ "Don't parallelize when you need to understand full system state" — decision criterion, not a behavior command
✅ "Don't use markdown. Write as flowing prose instead." — has positive alternative
✅ "Never use bullet points. Present information in complete sentences." — has alternative
