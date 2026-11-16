from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from assistant_api.db import ChatSession, Feedback, Interaction, Repository, hash_session, init_db, make_engine


@pytest.fixture
def repo():
    repository, engine = make_repo()
    yield repository
    engine.dispose()


def make_repo():
    engine = make_engine("sqlite://")
    init_db(engine)
    return Repository(engine, "salt"), engine


def test_session_id_is_hashed():
    repo, engine = make_repo()
    repo.record_interaction("student-42", "r1", "fee", None, True, False, 3.0)
    with Session(engine) as db:
        s = db.exec(select(ChatSession)).one()
    assert s.id == hash_session("student-42", "salt") and "student-42" not in s.id


def test_one_session_many_interactions():
    repo, engine = make_repo()
    for i in range(3):
        repo.record_interaction("s", f"r{i}", "rule", "H26-5.3", True, False, 10.0)
    with Session(engine) as db:
        assert len(db.exec(select(ChatSession)).all()) == 1
        assert len(db.exec(select(Interaction)).all()) == 3


def test_feedback_requires_existing_interaction():
    repo, _ = make_repo()
    assert repo.add_feedback("missing", 1, None) is None
    repo.record_interaction("s", "r1", "fee", None, True, False, 1.0)
    assert repo.add_feedback("r1", -1, "wrong fee").id == 1


def test_feedback_survives_reopening_database(tmp_path):
    url = f"sqlite:///{tmp_path / 'assistant.db'}"
    engine = make_engine(url)
    init_db(engine)
    repository = Repository(engine, "salt")
    repository.record_interaction("private-session", "r1", "fee", None, True, False, 2.0)
    saved = repository.add_feedback("r1", -1, "Please check the fee")
    assert saved.id is not None
    assert saved.created_at is not None
    engine.dispose()
    reopened = make_engine(url)
    try:
        rows = Repository(reopened, "salt").list_feedback()
        assert len(rows) == 1
        assert (rows[0].id, rows[0].request_id, rows[0].rating, rows[0].comment) == (
            saved.id,
            "r1",
            -1,
            "Please check the fee",
        )
    finally:
        reopened.dispose()


def test_feedback_order_and_limit(repo):
    assert repo.list_feedback() == []
    repo.record_interaction("s", "r1", "fee", None, True, False, 1.0)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with Session(repo.engine) as db:
        for day in (1, 3, 2):
            db.add(Feedback(request_id="r1", rating=0, comment=str(day), created_at=start + timedelta(days=day)))
        db.commit()
    assert [f.comment for f in repo.list_feedback()] == ["3", "2", "1"]
    assert [f.comment for f in repo.list_feedback(2)] == ["3", "2"]
    assert repo.list_feedback(0) == []


def test_unknown_feedback_does_not_write(repo):
    assert repo.add_feedback("missing", 1, None) is None
    assert repo.list_feedback() == []


def test_hash_is_stable_and_salted():
    assert hash_session("session", "salt") == hash_session("session", "salt")
    assert hash_session("session", "salt") != hash_session("session", "other")
    assert len(hash_session("session", "salt")) == 16
    assert "message" not in Interaction.__table__.columns
    assert "raw_session" not in Interaction.__table__.columns


def test_intent_statistics(repo):
    assert repo.intent_stats() == []
    repo.record_interaction("s", "r1", "fee", None, True, False, 10.0)
    repo.record_interaction("s", "r2", "fee", None, False, True, 21.1)
    repo.record_interaction("s", "r3", "office", None, True, False, 4.0)
    assert repo.intent_stats() == [
        {"intent": "fee", "requests": 2, "avg_latency_ms": 15.6, "unresolved": 1},
        {"intent": "office", "requests": 1, "avg_latency_ms": 4.0, "unresolved": 0},
    ]


def test_duplicate_request_rolls_back_new_session(repo):
    repo.record_interaction("original", "r1", "fee", None, True, False, 1.0)
    with pytest.raises(IntegrityError):
        repo.record_interaction("new-session", "r1", "fee", None, True, False, 1.0)
    with Session(repo.engine) as db:
        assert len(db.exec(select(Interaction)).all()) == 1
        assert db.get(ChatSession, hash_session("new-session", "salt")) is None
