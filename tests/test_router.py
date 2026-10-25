from assistant_core.models import Intent
from assistant_core.router import route

SAMPLE_OFFICES = {"library", "academic affairs", "student affairs"}


def test_route_greeting():
    assert route("hello", SAMPLE_OFFICES) == Intent.GREETING
    assert route("Xin Chao!", SAMPLE_OFFICES) == Intent.GREETING


def test_route_fee():
    assert route("What is my tuition fee?", SAMPLE_OFFICES) == Intent.FEE
    assert route("calculate fee for 18 credits", SAMPLE_OFFICES) == Intent.FEE


def test_route_office():
    assert route("Where is the library located?", SAMPLE_OFFICES) == Intent.OFFICE


def test_route_rule():
    assert route("How to defer an exam?", SAMPLE_OFFICES) == Intent.RULE
