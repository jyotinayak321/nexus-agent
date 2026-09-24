"""
llm_provider.py
---------------
Pluggable LLM adapter. Uses Groq when GROQ_API_KEY is available and a mock
provider for local UI/pipeline testing when it is not.
"""

import os
from groq import Groq


class BaseLLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GroqProvider(BaseLLMProvider):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("GROQ_API_KEY is not configured")
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content


class MockProvider(BaseLLMProvider):
    def generate(self, prompt: str) -> str:
        return f"[MOCK RESPONSE] Prompt received: {prompt[:140]}..."


def get_llm_provider() -> BaseLLMProvider:
    try:
        return GroqProvider()
    except ValueError:
        print("GROQ_API_KEY missing — MockProvider is active")
        return MockProvider()
