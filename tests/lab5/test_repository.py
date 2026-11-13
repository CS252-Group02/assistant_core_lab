"""Acceptance tests for the persistence repository."""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from assistant_api.db import ChatSession, Feedback, Interaction, hash_session


def record(repo, request_id="r1", **updates):
    values = dict(
        raw_session="private-session", request_id=request_id, intent="fee", topic=None,
        resolved=True, degraded=False, latency_ms=10.0,
    )
    repo.record_interaction(**(values | updates))


def test_hash_changes_with_salt():
    assert hash_session("session", "salt-a") != hash_session("session", "salt-b")


def test_saved_feedback_has_generated_fields(repo):
    record(repo)
    feedback = repo.add_feedback("r1", -1, "Please check the calculation")
    assert feedback is not None
    assert feedback.id is not None and feedback.id > 0
    assert feedback.request_id == "r1" and feedback.rating == -1
    assert feedback.comment == "Please check the calculation"
    assert isinstance(feedback.created_at, datetime)


def test_unknown_request_does_not_insert_feedback(repo, engine):
    assert repo.add_feedback("missing", 1, None) is None
    with Session(engine) as db:
        assert db.exec(select(Feedback)).all() == []


def test_list_feedback_newest_first_and_limited(repo, engine):
    record(repo)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with Session(engine) as db:
        db.add_all([
            Feedback(request_id="r1", rating=rating, created_at=base + timedelta(days=day))
            for day, rating in [(0, -1), (2, 1), (1, 0)]
        ])
        db.commit()
    assert [item.rating for item in repo.list_feedback(2)] == [1, 0]
    assert repo.list_feedback(0) == []


def test_empty_repository(repo):
    assert repo.list_feedback() == []
    assert repo.intent_stats() == []


def test_default_feedback_limit_is_100(repo, engine):
    record(repo)
    with Session(engine) as db:
        db.add_all([Feedback(request_id="r1", rating=0) for _ in range(105)])
        db.commit()
    assert len(repo.list_feedback()) == 100


def test_intent_stats_use_counts_and_average(repo):
    record(repo, "r1", latency_ms=10.0)
    record(repo, "r2", latency_ms=20.0, resolved=False, degraded=True)
    record(repo, "r3", intent="unknown", latency_ms=2.0, resolved=False)
    stats = {row["intent"]: row for row in repo.intent_stats()}
    assert stats == {
        "fee": {"intent": "fee", "requests": 2, "avg_latency_ms": 15.0, "unresolved": 1},
        "unknown": {"intent": "unknown", "requests": 1, "avg_latency_ms": 2.0, "unresolved": 1},
    }


def test_database_has_no_raw_message_or_session_columns(repo, engine):
    record(repo)
    assert "message" not in Interaction.__table__.columns
    assert "raw_session" not in ChatSession.__table__.columns
    with Session(engine) as db:
        saved = db.exec(select(ChatSession)).one()
        assert saved.id == hash_session("private-session", "test-salt")
