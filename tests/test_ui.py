import httpx

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note, validate_input

OK = {"answer": "Room B.201", "intent": "office", "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
      "degraded": False, "escalate": False, "path": "deterministic", "request_id": "abc123"}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    r = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert r.ok and r.answer == "Room B.201" and r.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)
    r = client_with(boom).ask("hi", "s1")
    assert not r.ok and "backend" in r.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


def test_format_sources():
    assert format_sources([]) == ""
    assert format_sources(OK["sources"]) == "Sources: S26#1 — 1 Library borrowing"


def test_status_note():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True))
    assert status_note(ChatResult(ok=True)) is None


def test_format_multiple_sources():
    sources = [
        {"id": "S26#1", "title": "1 Library borrowing"},
        {"id": "H26#5.3", "title": "5.3 Thesis registration"},
    ]
    assert format_sources(sources) == (
        "Sources: S26#1 — 1 Library borrowing; H26#5.3 — 5.3 Thesis registration"
    )


def test_status_note_degraded():
    assert status_note(ChatResult(ok=True, degraded=True)) == (
        "Shown directly from the source document (the AI helper was unavailable)."
    )


def test_status_note_escalation_takes_priority_over_degraded():
    note = status_note(ChatResult(ok=True, escalate=True, degraded=True))
    assert note == status_note(ChatResult(ok=True, escalate=True))
    assert note is not None and "Training Office" in note
    assert note != status_note(ChatResult(ok=True, degraded=True))
