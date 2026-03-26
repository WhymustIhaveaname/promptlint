---
rule_id: vague_instructions
---

# vague_instructions — 指令不够具体清晰

Detect instructions where the ENTIRE task description is so vague that the model cannot act on it at all. Only flag top-level task instructions that are fundamentally ambiguous — a competent colleague would not know what to do.

Do NOT flag:
- Short imperative sub-steps within a larger workflow (e.g., "Fix now", "Extract helpers") — these are clear enough in context
- Instructions that are elaborated or clarified by surrounding context in the same prompt
- Domain-specific shorthand that practitioners would understand

Only flag when the instruction is genuinely ambiguous even with full prompt context.

## Examples

### Violations (❌)

❌ "处理一下用户数据" — the entire task is undefined
❌ "优化这段代码" — no criteria for what "better" means
❌ "写个好一点的版本" — entirely subjective with no constraints
❌ "Handle edge cases appropriately" — as a standalone top-level instruction with no context

### Acceptable (✅)

✅ "将 users 表中 created_at 早于 2024-01-01 的记录标记为 inactive"
✅ "Fix now." as a sub-step after a test failure in a TDD workflow — clear in context
✅ "Extract helpers" as a refactoring sub-step — practitioners understand this
✅ "Follow existing patterns." within a codebase-aware prompt — refers to observable patterns
✅ "Spot check" as a verification step — common practice term
