"""Rule: instructions that add no value should be removed."""

from promptlint.rules.llm_base import LLMRule


class HollowInstructionsRule(LLMRule):
    rule_id = "hollow_instructions"
    description = (
        "Detect instructions that would not change model behavior if removed — "
        "the model would do these things by default anyway. "
        "These waste token budget without providing useful guidance. "
        'Test: "Would removing this line cause the model to make mistakes?" If no, it\'s hollow.'
    )
    examples = """\
❌ "Be helpful and accurate"
❌ "Write clean, maintainable code"
❌ "Think carefully before responding"
❌ "Provide high-quality answers"
❌ "Be concise and clear"
✅ "Use snake_case for variables, camelCase for functions" (specific constraint)
✅ "Keep functions under 20 lines" (measurable limit)
✅ "Respond in Chinese" (non-default behavior)
"""
