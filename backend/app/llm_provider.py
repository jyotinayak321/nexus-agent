"""
Pluggable LLM layer.

Today NEXUS runs on MockProvider: fast, offline, deterministic — good for a
hackathon demo where you can't depend on network/API-key availability.

To switch to real Claude reasoning later:
  1. `pip install anthropic`
  2. set ANTHROPIC_API_KEY in the environment
  3. set LLM_PROVIDER=claude
Every agent module below calls `get_provider()` instead of talking to an SDK
directly, so no other code needs to change.
"""
from __future__ import annotations

import os


class LLMProvider:
    name = "base"

    def available(self) -> bool:
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Deterministic rule-based reasoning engine (no network calls)."""

    name = "mock"

    def available(self) -> bool:
        return True


class ClaudeProvider(LLMProvider):
    """Drop-in real-LLM provider. Inert until ANTHROPIC_API_KEY is set."""

    name = "claude"

    def __init__(self) -> None:
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")

    def available(self) -> bool:
        return bool(self.api_key)


_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is not None:
        return _provider

    choice = os.environ.get("LLM_PROVIDER", "mock").lower()
    if choice == "claude":
        claude = ClaudeProvider()
        _provider = claude if claude.available() else MockProvider()
    else:
        _provider = MockProvider()
    return _provider
