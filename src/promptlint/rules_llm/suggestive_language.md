---
rule_id: suggestive_language
---

# suggestive_language — 建议性语言用于需要行动的场景

In prompts that instruct a model to perform actions, suggestive/tentative language (e.g. 'Can you suggest...', 'Maybe you could...', 'Would it be possible to...') should be replaced with direct action verbs.

Note: suggestive language in examples, quotes, or user-facing templates is OK.

## Examples

❌ "Can you suggest some changes to improve this function?"
❌ "Maybe you could refactor the login module?"
❌ "Would it be possible to add error handling?"
✅ "Refactor the login module to use async/await."
✅ "Add error handling for network timeouts in this function."
