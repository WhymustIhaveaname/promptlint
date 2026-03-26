---
rule_id: style_mismatch
---

# style_mismatch — prompt 风格与期望输出不一致

The prompt's own writing style influences the model's output style. If the prompt is written in markdown, the output will tend to be markdown too. If the prompt is in English but expects Chinese output, that's a mismatch. Check if the prompt's formatting, language, and tone match the expected output.

## Examples

❌ Prompt written in heavy markdown (headers, lists, bold), but expects plain text conversation output
❌ Prompt written in formal academic English, but expects casual Chinese chat
❌ Prompt written in English, but expects Chinese output without explicitly saying so
✅ Prompt style and language match the expected output
