"""Acceptance tests for database settings and environment mappings."""

import pytest

from assistant_core.config import Settings, load_settings


def test_database_defaults():
    assert Settings().database_url == "sqlite:///assistant.db"


def test_database_loader_defaults(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SESSION_SALT", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    settings = load_settings(env_file=None)
    assert settings.database_url == "sqlite:///assistant.db"
    assert settings.session_salt == "dev-only-change-me"
    assert settings.session_salt not in repr(settings)


def test_database_environment(monkeypatch, tmp_path):
    url = f"sqlite:///{(tmp_path / 'local.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("SESSION_SALT", "private-test-salt")
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    settings = load_settings(env_file=None)
    assert settings.database_url == url
    assert settings.session_salt == "private-test-salt"
    assert "private-test-salt" not in repr(settings)


@pytest.mark.parametrize("override", [False, True])
def test_database_dotenv_and_environment_precedence(monkeypatch, tmp_path, override):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///from-file.db\nSESSION_SALT=file-test-salt\n", encoding="utf-8")
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    for key, value in [("DATABASE_URL", "sqlite:///from-env.db"), ("SESSION_SALT", "env-test-salt")]:
        monkeypatch.delenv(key, raising=False)
        if override:
            monkeypatch.setenv(key, value)
    settings = load_settings(env_file=str(env_file))
    assert settings.database_url == ("sqlite:///from-env.db" if override else "sqlite:///from-file.db")
    assert settings.session_salt == ("env-test-salt" if override else "file-test-salt")
    assert settings.session_salt not in repr(settings)
