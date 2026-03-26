"""Rule: negative instructions should include a positive alternative."""

from promptlint.rules.llm_base import LLMRule


class NegativeOnlyRule(LLMRule):
    rule_id = "negative_only"
    description = (
        "Detect instructions that only say what NOT to do without providing a positive alternative. "
        "The model needs a positive target to replace the forbidden behavior. "
        "Just saying 'Don't do X' leaves the model uncertain about what to do instead."
    )
    examples = """\
❌ "Do not use markdown formatting" → ✅ "Write your response as smoothly flowing prose paragraphs"
❌ "Don't make up information" → ✅ "Only answer based on the provided documents. If the answer isn't there, say 'I don't have that information'"
❌ "Never use bullet points" → ✅ "Present information in complete sentences within paragraphs"
"""
