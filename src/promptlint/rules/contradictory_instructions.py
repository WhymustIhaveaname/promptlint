"""Rule: instructions in the prompt should not contradict each other."""

from promptlint.rules.llm_base import LLMRule


class ContradictoryInstructionsRule(LLMRule):
    rule_id = "contradictory_instructions"
    description = (
        "Detect pairs of instructions that contradict each other. "
        "Contradictions force the model to spend reasoning tokens reconciling conflicts "
        "instead of performing the actual task, degrading output quality."
    )
    examples = """\
❌ "Always respond in JSON format." + "Write your answer as a natural paragraph."
❌ "Keep responses under 100 words." + "Provide comprehensive, detailed explanations."
❌ "Never use external tools." + "Search the web when you don't know the answer."
"""
