"""
Tests for English output enforcement and language boundary constraints.
"""
import unittest
import re
from llm_provider import MockProvider
from agents.research_agent import research_agent
from agents.planning_agent import planning_agent
from agents.risk_agent import risk_agent
from agents.decision_agent import decision_agent

def contains_devanagari(text: str) -> bool:
    """Returns True if any Devanagari Unicode characters (Hindi/Sanskrit) exist in the text."""
    return bool(re.search(r'[\u0900-\u097F]', text))

class TestLanguageEnforcement(unittest.TestCase):
    def test_mock_provider_returns_strict_english_for_plan(self):
        provider = MockProvider()
        prompt = "Compare AI agent frameworks: LangChain, LangGraph, and AutoGPT. Generate actionable tasks and plan."
        response = provider.generate(prompt)
        
        self.assertFalse(
            contains_devanagari(response),
            f"MockProvider output must not contain Hindi/Devanagari characters. Found in: {response}"
        )
        self.assertIn("Phase", response)
        self.assertIn("Deliverable", response)
        self.assertIn("pgvector", response)

    def test_mock_provider_returns_strict_english_for_decision(self):
        provider = MockProvider()
        prompt = "Compare framework recommendation and weighted scoring decision"
        response = provider.generate(prompt)
        
        self.assertFalse(
            contains_devanagari(response),
            f"MockProvider output must not contain Hindi/Devanagari characters. Found in: {response}"
        )
        self.assertIn("Weighted", response)
        self.assertIn("LangGraph", response)
        self.assertIn("LangChain", response)
        self.assertIn("AutoGPT", response)

    def test_mock_provider_returns_strict_english_even_with_hindi_prompt(self):
        provider = MockProvider()
        hindi_prompt = "AI agent frameworks की तुलना करें और plan बनाएं (Compare AI agent frameworks)"
        response = provider.generate(hindi_prompt)
        
        self.assertFalse(
            contains_devanagari(response),
            f"MockProvider output must not contain Hindi/Devanagari characters. Found in: {response}"
        )

    def test_agent_prompts_contain_strict_english_directive(self):
        """Inspect agent modules to verify the English language rule is strictly specified."""
        import inspect
        
        for name, agent_func in [
            ("research_agent", research_agent),
            ("planning_agent", planning_agent),
            ("risk_agent", risk_agent),
            ("decision_agent", decision_agent),
        ]:
            src = inspect.getsource(agent_func)
            self.assertIn(
                "English",
                src,
                f"Agent {name} must have explicit English language instruction in its source code."
            )
            # Ensure no hardcoded Hindi strings are in the agent source files
            self.assertFalse(
                contains_devanagari(src),
                f"Agent {name} source code contains leftover Hindi characters!"
            )

if __name__ == "__main__":
    unittest.main()
