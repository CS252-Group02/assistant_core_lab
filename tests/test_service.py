"""Step 9 service behavior using real tools, knowledge, and offline responders."""

import logging

import pytest

from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


@pytest.fixture
def service() -> AssistantService:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    settings = Settings(data_dir=data_dir)
    offices = OfficeDirectory.from_csv(data_dir / "offices.csv")
    handbook = Handbook.from_json(data_dir / "handbook.json")

    return AssistantService(
        settings,
        offices,
        handbook,
        StubLLMResponder(fail=False),
    )

from assistant_core.models import Intent, Message, Source
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService


def test_greeting(service: AssistantService) -> None:
    r = service.handle(Message(text="hello"))
    assert r.intent is Intent.GREETING
    assert r.answer == "Hello! I can help with offices, fees and rules."
    assert r.degraded is False


@pytest.mark.parametrize(
    ("text", "amount"),
    [
        ("tuition for 18 credits and 2 retake", "9,450,000 VND"),
        ("tuition for 15 credits", "6,750,000 VND"),
    ],
)
def test_tuition(service: AssistantService, text: str, amount: str) -> None:
    r = service.handle(Message(text=text))
    assert r.intent is Intent.FEE
    assert r.answer == f"Your tuition is {amount}."
    assert r.degraded is False


def test_tuition_uses_configured_rates(service: AssistantService) -> None:
    service.settings.credit_rate_vnd = 500_000
    service.settings.retake_multiplier = 2.0
    r = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert r.intent is Intent.FEE
    assert r.answer == "Your tuition is 11,000,000 VND."


@pytest.mark.parametrize(
    ("text", "error"),
    [
        ("tuition fee", "How many credits?"),
        ("tuition for 2 retake", "How many credits?"),
        ("tuition for 0 credits", "Credits must be between 1 and 30."),
        ("tuition for 31 credits", "Credits must be between 1 and 30."),
    ],
)
def test_invalid_tuition(service: AssistantService, text: str, error: str) -> None:
    r = service.handle(Message(text=text))
    assert r.intent is Intent.FEE
    assert r.answer == error
    assert r.degraded is False


def test_tuition_uses_configured_maximum(service: AssistantService) -> None:
    service.settings.max_credits = 20
    r = service.handle(Message(text="tuition for 21 credits"))
    assert r.intent is Intent.FEE
    assert r.answer == "Credits must be between 1 and 20."


def test_office_lookup(service: AssistantService) -> None:
    r = service.handle(Message(text="where is the library"))
    assert r.intent is Intent.OFFICE
    assert r.answer == "Library: room B.201, open Mon-Sat 07:00-20:00."
    assert r.degraded is False


def test_missing_office_is_safe(service: AssistantService, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service.offices, "find", lambda text: None)
    r = service.handle(Message(text="where is the library"))
    assert r.intent is Intent.UNKNOWN
    assert r.answer == "Sorry, I don't know that yet."
    assert r.sources == []
    assert r.degraded is False


def test_handbook_lookup(service: AssistantService) -> None:
    text = "thesis registration credits"
    rule = service.handbook.search(text)
    assert rule is not None
    r = service.handle(Message(text=text))
    assert r.intent is Intent.RULE
    assert r.sources == [Source(id="H26-5.3", title="Thesis registration")]
    assert r.answer == StubLLMResponder(fail=False).explain(text, rule)
    assert r.degraded is False


def test_unknown_question(service: AssistantService) -> None:
    r = service.handle(Message(text="how is the cafeteria food?"))
    assert r.intent is Intent.UNKNOWN
    assert r.answer == "Sorry, I don't know that yet."
    assert r.sources == []
    assert r.degraded is False


def test_fallback_when_provider_fails(service: AssistantService, caplog: pytest.LogCaptureFixture) -> None:
    service.responder = StubLLMResponder(fail=True)
    text = "thesis registration credits"
    rule = service.handbook.search(text)
    assert rule is not None

    with caplog.at_level(logging.WARNING, logger="assistant_core.service"):
        r = service.handle(Message(text="thesis registration credits"))

    assert r.degraded and r.sources
    assert r.intent is Intent.RULE
    assert r.answer == TemplateResponder().explain(text, rule)
    assert r.sources == [Source(id="H26-5.3", title="Thesis registration")]
    assert caplog.record_tuples == [
        ("assistant_core.service", logging.WARNING, "provider failed; using template fallback")
    ]


def test_unexpected_responder_error_propagates(service: AssistantService, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(question, rule):
        raise ValueError("unexpected responder bug")

    monkeypatch.setattr(service.responder, "explain", fail)
    with pytest.raises(ValueError, match="unexpected responder bug"):
        service.handle(Message(text="thesis registration credits"))
