"""Acceptance tests for API persistence integration; no external requests."""

from sqlmodel import Session, select

from assistant_api.db import ChatSession, Interaction, Repository, hash_session, init_db, make_engine

ADMIN = {"X-API-Key": "test-admin"}


def send_chat(client, message="hello", session_id="private-session"):
    response = client.post("/v1/chat", json={"message": message, "session_id": session_id})
    assert response.status_code == 200, response.text
    return response.json()


def test_chat_records_metadata(lab_client, engine):
    body = send_chat(lab_client)
    with Session(engine) as db:
        saved = db.exec(select(Interaction)).one()
        session = db.exec(select(ChatSession)).one()
    assert saved.request_id == body["request_id"]
    assert saved.intent == body["intent"] == "greeting"
    assert saved.resolved is True and saved.degraded is False
    assert saved.latency_ms >= 0 and saved.created_at is not None
    assert session.id == saved.session_id == hash_session("private-session", "test-salt")


def test_unknown_chat_is_unresolved(lab_client, engine):
    body = send_chat(lab_client, "how is the cafeteria food?")
    assert body["intent"] == "unknown"
    with Session(engine) as db:
        assert db.exec(select(Interaction)).one().resolved is False


def test_rule_topic_matches_first_source(lab_client, engine):
    body = send_chat(lab_client, "thesis registration credits")
    assert body["sources"]
    with Session(engine) as db:
        assert db.exec(select(Interaction)).one().topic == body["sources"][0]["id"]


def test_degraded_response_is_recorded(client_factory, repo, engine, monkeypatch):
    from assistant_core.models import Intent, Response, Source
    from assistant_core.service import AssistantService

    def fallback(self, message):
        return Response(
            answer="Fallback answer", intent=Intent.RULE, degraded=True,
            sources=[Source(id="H26-5.3", title="Thesis registration")],
        )

    monkeypatch.setattr(AssistantService, "handle", fallback)
    with client_factory(repo) as client:
        assert send_chat(client)["degraded"] is True
    with Session(engine) as db:
        saved = db.exec(select(Interaction)).one()
        assert saved.degraded is True and saved.resolved is True


def test_feedback_limit_reaches_repository(lab_client, repo):
    repo.record_interaction("s", "r1", "greeting", None, True, False, 1.0)
    repo.add_feedback("r1", 1, "First")
    repo.add_feedback("r1", -1, "Second")
    response = lab_client.get("/v1/feedback?limit=1", headers=ADMIN)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_invalid_chat_does_not_create_interaction(lab_client, engine):
    assert lab_client.post("/v1/chat", json={"message": ""}).status_code == 422
    with Session(engine) as db:
        assert db.exec(select(Interaction)).all() == []


def test_feedback_roundtrip(lab_client):
    rid = send_chat(lab_client)["request_id"]
    response = lab_client.post("/v1/feedback", json={"request_id": rid, "rating": 1, "comment": "Helpful"})
    assert response.status_code == 201
    saved = response.json()
    assert saved["id"] > 0 and saved["created_at"]
    listed = lab_client.get("/v1/feedback", headers=ADMIN)
    assert listed.status_code == 200 and listed.json() == [saved]


def test_unknown_feedback_returns_error_envelope(lab_client):
    response = lab_client.post("/v1/feedback", json={"request_id": "missing", "rating": -1})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "unknown_request_id"


def test_feedback_validation(lab_client):
    for payload in [
        {"request_id": "r1", "rating": 5},
        {"request_id": "r1", "rating": 1, "comment": "x" * 501},
    ]:
        response = lab_client.post("/v1/feedback", json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_request"


def test_admin_endpoints_require_key(lab_client):
    for path in ["/v1/feedback", "/v1/stats/intents"]:
        assert lab_client.get(path).status_code == 401
        assert lab_client.get(path, headers={"X-API-Key": "wrong"}).status_code == 401


def test_stats_and_feedback_use_injected_repository(lab_client, repo):
    repo.record_interaction("s", "existing", "fee", None, True, False, 12.0)
    stats = lab_client.get("/v1/stats/intents", headers=ADMIN)
    assert stats.status_code == 200
    assert stats.json() == [{"intent": "fee", "requests": 1, "avg_latency_ms": 12.0, "unresolved": 0}]
    assert lab_client.post("/v1/feedback", json={"request_id": "existing", "rating": 0}).status_code == 201
    assert len(repo.list_feedback()) == 1


def test_feedback_survives_new_app_and_engine(tmp_path, client_factory):
    url = f"sqlite:///{(tmp_path / 'restart.db').as_posix()}"
    first = make_engine(url)
    init_db(first)
    try:
        with client_factory(Repository(first, "test-salt")) as client:
            rid = send_chat(client)["request_id"]
            response = client.post("/v1/feedback", json={"request_id": rid, "rating": 1})
            assert response.status_code == 201
            saved = response.json()
    finally:
        first.dispose()
    second = make_engine(url)
    try:
        with client_factory(Repository(second, "test-salt")) as client:
            response = client.get("/v1/feedback", headers=ADMIN)
            assert response.status_code == 200 and response.json() == [saved]
    finally:
        second.dispose()


def test_default_app_uses_database_settings(tmp_path, lab_settings, client_factory):
    url = f"sqlite:///{(tmp_path / 'configured.db').as_posix()}"
    settings = lab_settings.model_copy(update={"database_url": url, "session_salt": "test-salt"})
    with client_factory(settings=settings) as client:
        send_chat(client)
    assert (tmp_path / "configured.db").exists()
    engine = make_engine(url)
    try:
        with Session(engine) as db:
            assert len(db.exec(select(Interaction)).all()) == 1
    finally:
        engine.dispose()
