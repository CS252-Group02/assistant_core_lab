"""Response generation behind one interface (Step 8).

The LLM is a replaceable component behind the Responder protocol (adapter
pattern). The service only depends on Responder, so a real provider can be
added in Week 4 without changing the service.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from assistant_core.errors import ProviderError

if TYPE_CHECKING:
    from assistant_core.knowledge import Rule

__all__ = [
    "Responder",
    "StubLLMResponder",
    "TemplateResponder",
]


class Responder(Protocol):
    """Anything that can explain a handbook rule in answer to a question."""

    def explain(self, question: str, rule: Rule) -> str: ...


class TemplateResponder:
    """Deterministic responder with no AI; also used as the fallback."""

    def explain(self, question: str, rule: Rule) -> str:
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Stand-in for an LLM provider that can simulate an outage.

    No random failures, no sleeping, no API key: tests stay offline and deterministic.
    """

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"


def make_responder(provider: str) -> Responder:
    if provider == "stub":
        return StubLLMResponder()
    if provider == "template":
        return TemplateResponder()
    raise ProviderError(f"unknown provider {provider!r} (real providers arrive in Week 4)")
