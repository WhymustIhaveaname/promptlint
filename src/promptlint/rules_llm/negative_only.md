---
rule_id: negative_only
---

# negative_only — 只有否定没有正向替代

Detect isolated imperative instructions that prohibit a core behavior without giving ANY positive alternative anywhere in the prompt. Only flag when the prohibition is a standalone top-level output instruction and the model would be left with no idea what to do instead.

Only flag when ALL of these are true:
- The instruction directly controls the model's output behavior (format, content, style)
- There is no positive alternative ANYWHERE nearby in the prompt (not just the same sentence)
- Removing the prohibition would leave the model with no guidance

Do NOT flag:
- Guardrail lists / "Never do X" constraint sections — these define boundaries and the model knows the default (do nothing)
- Decision criteria ("Don't parallelize when...")
- Safety constraints ("Never force-push", "Don't skip reviews")
- Process rules that tell the model what NOT to do in a workflow — the workflow itself is the positive guidance
- Negative instructions followed by a positive alternative anywhere in the same section

## Examples

❌ "Do not use markdown formatting" (alone, no alternative anywhere) → should say "Write as prose paragraphs"
❌ "Don't make up information" (entire prompt gives no sourcing guidance) → should say "Only answer based on provided documents"
✅ "Never force-push without explicit request" — safety guardrail, no alternative needed
✅ "Don't skip reviews" — process constraint within a workflow
✅ "Don't dispatch multiple agents in parallel" — boundary rule, default is sequential
✅ A "Never" list defining project guardrails — these are constraints, not output instructions
