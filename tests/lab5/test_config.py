"""Acceptance tests for database settings and environment mappings."""

from assistant_core.config import Settings, load_settings


def test_database_defaults():
    assert Settings().database_url == "sqlite:///assistant.db"


def test_database_environment(monkeypatch, tmp_path):
    url = f"sqlite:///{(tmp_path / 'local.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("SESSION_SALT", "private-test-salt")
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    settings = load_settings(env_file=None)
    assert settings.database_url == url
    assert settings.session_salt == "private-test-salt"
    assert "private-test-salt" not in repr(settings)
