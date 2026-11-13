"""Offline fixtures for the Lab 5 acceptance suite."""

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.config import Settings
from assistant_core.service import build_service

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def lab_settings():
    return Settings(
        data_dir=ROOT / "data", llm_provider="stub", api_admin_key="test-admin", rate_limit_per_min=100
    )


@pytest.fixture
def engine():
    engine = make_engine("sqlite://")
    init_db(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def repo(engine):
    return Repository(engine, "test-salt")


@pytest.fixture
def client_factory(lab_settings):
    """Each context creates and closes an app and a mocked weather client."""
    from contextlib import contextmanager

    @contextmanager
    def open_client(repository=None, settings=None):
        selected = settings or lab_settings
        weather = WeatherClient(
            "https://weather.test/forecast",
            selected.campus_lat,
            selected.campus_lon,
            transport=httpx.MockTransport(lambda request: httpx.Response(503)),
        )
        try:
            app = create_app(selected, build_service(selected), weather, repo=repository)
            with TestClient(app) as client:
                yield client
        finally:
            weather._client.close()

    return open_client


@pytest.fixture
def lab_client(client_factory, repo):
    with client_factory(repo) as client:
        yield client
