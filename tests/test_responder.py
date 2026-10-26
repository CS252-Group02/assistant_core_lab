from dataclasses import dataclass

import pytest

from assistant_core.errors import ProviderError
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder


@dataclass(frozen=True)
class FakeRule:
    id: str
    title: str
    text: str


RULE = FakeRule(
    id="H26-5.3",
    title="Thesis registration",
    text="Students may register a thesis when they have at least 120 accumulated credits and a GPA of at least 2.0.",
)


def test_template_responder():
    answer = TemplateResponder().explain("thesis registration credits", RULE)
    assert answer == f"Thesis registration: {RULE.text}"


def test_stub_responder_success():
    answer = StubLLMResponder().explain("thesis registration credits", RULE)
    assert answer == f"Based on 'Thesis registration': {RULE.text}"


def test_stub_responder_is_deterministic():
    responder = StubLLMResponder()
    answers = {responder.explain("thesis", RULE) for _ in range(20)}
    assert len(answers) == 1


def test_stub_responder_failure():
    with pytest.raises(ProviderError):
        StubLLMResponder(fail=True).explain("thesis registration credits", RULE)


def test_responders_share_interface():
    responders: list[Responder] = [TemplateResponder(), StubLLMResponder()]
    for responder in responders:
        assert RULE.text in responder.explain("thesis", RULE)
