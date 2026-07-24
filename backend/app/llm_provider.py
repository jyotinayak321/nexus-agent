"""
Pluggable LLM layer.

MockProvider: fast, offline, deterministic — the default fallback so NEXUS
always works even with no API key (e.g. offline demo).

GroqProvider: real LLM reasoning via Groq's hosted inference API. Activates
automatically when GROQ_API_KEY is set (see backend/.env). Used today by the
RAG research-query endpoint to synthesize an answer from retrieved chunks;
the rule-based debate/decomposition agents are untouched so the core demo
stays deterministic.

Every caller goes through get_provider().generate(...) instead of talking to
an SDK directly, so swapping providers never touches calling code.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class LLMProvider:
    name = "base"

    def available(self) -> bool:
        raise NotImplementedError

    def generate(self, system: str, user: str, max_tokens: int = 600) -> str:
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Deterministic offline fallback — no network calls."""

    name = "mock"

    def available(self) -> bool:
        return True

    def generate(self, system: str, user: str, max_tokens: int = 600) -> str:
        return (
            "[offline mode — no LLM configured] Here is the raw retrieved context, "
            "unsummarized:\n\n" + user
        )


class GroqProvider(LLMProvider):
    """Real LLM reasoning via Groq's hosted inference API."""

    name = "groq"
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self) -> None:
        self.api_key = os.environ.get("GROQ_API_KEY")
        self._client = None

    def available(self) -> bool:
        return bool(self.api_key)

    def _client_or_raise(self):
        if self._client is None:
            from groq import Groq

            self._client = Groq(api_key=self.api_key)
        return self._client

    def generate(self, system: str, user: str, max_tokens: int = 600) -> str:
        client = self._client_or_raise()
        resp = client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return resp.choices[0].message.content


_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is not None:
        return _provider

    choice = os.environ.get("LLM_PROVIDER", "mock").lower()
    if choice == "groq":
        groq_provider = GroqProvider()
        _provider = groq_provider if groq_provider.available() else MockProvider()
    else:
        _provider = MockProvider()
    return _provider
