"""API tests run in process, with no server or external network calls."""

from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.config import Settings
from assistant_core.service import AssistantService, build_service

OK_JSON = {
    "current": {
        "temperature_2m": 28.5,
        "wind_speed_10m": 6.0,
        "weather_code": 0,
        "time": "2026-10-31T12:00",
    }
}


@pytest.fixture
def settings() -> Settings:
    return Settings(data_dir=Path(__file__).resolve().parent.parent / "data", llm_provider="stub")


@pytest.fixture
def service(settings: Settings) -> AssistantService:
    return build_service(settings)


@pytest.fixture
def client(settings: Settings, service: AssistantService) -> Iterator[TestClient]:
    weather = WeatherClient(
        "https://weather.test/forecast",
        settings.campus_lat,
        settings.campus_lon,
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json=OK_JSON)),
    )
    try:
        with TestClient(create_app(settings, service, weather)) as test_client:
            yield test_client
    finally:
        weather._client.close()


def test_offices_status_ok(client: TestClient) -> None:
    response = client.get("/v1/offices")
    assert response.status_code == 200


def test_offices_includes_library(client: TestClient) -> None:
    response = client.get("/v1/offices")
    assert any(office["name"] == "Library" for office in response.json())


def test_chat_validation_error(client: TestClient) -> None:
    response = client.post("/v1/chat", json={"message": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_rate_limit(client: TestClient, settings: Settings) -> None:
    for _ in range(settings.rate_limit_per_min):
        response = client.post("/v1/chat", json={"message": "Where is the Library?"})
        assert response.status_code == 200

    response = client.post("/v1/chat", json={"message": "Where is the Library?"})
    assert response.status_code == 429
    assert response.json()["error"] == {
        "code": "too_many_requests",
        "message": "Too many requests",
    }


def test_weather_uses_mock_response(client: TestClient) -> None:
    response = client.get("/v1/weather")
    assert response.status_code == 200
    assert response.json() == {
        "temperature_c": 28.5,
        "wind_kmh": 6.0,
        "description": "clear sky",
        "observed_at": "2026-10-31T12:00",
        "stale": False,
    }
