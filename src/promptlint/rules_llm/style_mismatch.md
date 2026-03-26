---
rule_id: style_mismatch
---

# style_mismatch — prompt 风格与期望输出不一致

Detect cases where the prompt's language fundamentally conflicts with the expected output language — specifically, when the prompt explicitly requests output in a different language than it is written in, without acknowledging this. Markdown formatting in a system prompt or skill definition is normal and should NOT be flagged.

IMPORTANT: System prompts, skill definitions, and instruction documents are commonly written in structured markdown. This is standard practice, NOT a style mismatch. Only flag language mismatches where the prompt writes in one language but expects output in another without saying so.

## Examples

### Violations (❌)

❌ Prompt written entirely in English, but says "请用中文回答" with no other Chinese context
❌ Prompt written in formal academic English, but expects casual Chinese chat output

### Acceptable (✅)

✅ Skill definition using markdown headers, lists, bold — this is normal for instruction documents
✅ English system prompt that expects English output — no mismatch
✅ Bilingual prompt that mixes English and Chinese naturally
✅ Prompt using markdown structure for its own organization, regardless of expected output format
