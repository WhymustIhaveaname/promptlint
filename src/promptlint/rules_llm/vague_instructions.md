---
rule_id: vague_instructions
---

# vague_instructions — 指令不够具体清晰

Detect instructions that are too vague for a model to act on reliably. Golden rule (Anthropic): show the prompt to a colleague unfamiliar with the task — if they'd be confused, the model will be too. Vague instructions force the model to guess intent.

## Examples

❌ "处理一下用户数据"
❌ "优化这段代码"
❌ "写个好一点的版本"
❌ "Handle edge cases appropriately"
✅ "将 users 表中 created_at 早于 2024-01-01 的记录标记为 inactive"
✅ "将这个 O(n²) 的嵌套循环改为使用 hash map，降低到 O(n)"
