"""
Tests for Budget and Deadline validation and cost calculation.
"""
import unittest
from budget_service import (
    validate_goal_inputs,
    estimate_tokens,
    calculate_cost_and_budget,
)

class TestBudgetService(unittest.TestCase):
    def test_valid_inputs(self):
        validate_goal_inputs("Compare AI agent frameworks", 50.0, 14)
        validate_goal_inputs("Valid research objective", None, None)
        validate_goal_inputs("Goal with zero budget", 0.0, 7)

    def test_negative_budget_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_goal_inputs("Compare frameworks", -10.0, 7)
        self.assertIn("Budget cannot be negative", str(ctx.exception))

    def test_invalid_deadline_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_goal_inputs("Compare frameworks", 100.0, 0)
        self.assertIn("Deadline must be at least 1 day", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_goal_inputs("Compare frameworks", 100.0, -5)
        self.assertIn("Deadline must be at least 1 day", str(ctx.exception))

    def test_short_goal_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_goal_inputs("ab", 100.0, 5)
        self.assertIn("at least 3 characters", str(ctx.exception))

    def test_estimate_tokens(self):
        text = "Hello world! This is a test for token estimation."
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 0)
        self.assertEqual(tokens, max(1, len(text) // 4))

    def test_calculate_cost_and_budget_within(self):
        state = {
            "goal": "Compare LangChain and LangGraph",
            "task_plan": "Step 1: Ingest documents into pgvector.\nStep 2: Compare LangChain and LangGraph."
        }
        result = calculate_cost_and_budget(state, budget=10.0, deadline_days=15)
        self.assertEqual(result["budget_limit_usd"], 10.0)
        self.assertEqual(result["budget_status"], "within_budget")
        self.assertEqual(result["deadline_days"], 15)
        self.assertEqual(result["deadline_status"], "feasible")
        self.assertGreater(result["estimated_tokens"], 0)
        self.assertGreater(result["estimated_cost_usd"], 0.0)

    def test_calculate_cost_and_budget_exceeded(self):
        state = {
            "goal": "A very long detailed architectural implementation plan " * 100
        }
        result = calculate_cost_and_budget(state, budget=0.0000001, deadline_days=2)
        self.assertEqual(result["budget_status"], "exceeded")
        self.assertEqual(result["deadline_status"], "at_risk")

    def test_calculate_cost_zero_budget(self):
        state = {"goal": "Sample execution plan"}
        result = calculate_cost_and_budget(state, budget=0.0, deadline_days=10)
        self.assertEqual(result["budget_status"], "zero_budget")
        self.assertEqual(result["deadline_status"], "tight")

if __name__ == "__main__":
    unittest.main()
