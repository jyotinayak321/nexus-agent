"""
Tests for FastAPI application endpoints, input validation, and plan responses.
"""
import unittest
from fastapi.testclient import TestClient
from main import app

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "nexus-backend")
        self.assertIn("database", data)

    def test_create_goal_negative_budget_rejected(self):
        response = self.client.post("/goal", json={
            "goal": "Test goal with negative budget",
            "budget": -50.0,
            "deadline_days": 10
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Budget cannot be negative", response.json().get("detail", ""))

    def test_create_goal_invalid_deadline_rejected(self):
        response = self.client.post("/goal", json={
            "goal": "Test goal with invalid deadline",
            "budget": 100.0,
            "deadline_days": 0
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Deadline must be at least 1 day", response.json().get("detail", ""))

    def test_create_goal_valid(self):
        response = self.client.post("/goal", json={
            "goal": "Compare LangChain and LangGraph for production multi-agent system",
            "budget": 250.0,
            "deadline_days": 14
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("goal_id", data)
        self.assertEqual(data.get("status"), "created")

    def test_get_nonexistent_plan(self):
        response = self.client.get("/plan/9999999")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
