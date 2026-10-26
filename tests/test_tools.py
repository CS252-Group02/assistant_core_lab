"""Unit tests for tools.py (credit parsing and tuition calculation - Step 6)."""

from __future__ import annotations

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_with_retake() -> None:
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_without_retake() -> None:
    assert parse_credits("tuition for 15 credits") == (15, 0)


def test_parse_retake_first() -> None:
    assert parse_credits("tuition for 2 retake and 18 credits") == (18, 2)


def test_parse_without_credits() -> None:
    with pytest.raises(InvalidRequest, match="How many credits?"):
        parse_credits("tuition fee")


def test_tuition_value() -> None:
    # Characterisation test: 18 credits + 2 retakes = 9,450,000 VND
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


def test_tuition_without_retake() -> None:
    assert tuition(15, 0, 450_000, 1.5, 30) == 6_750_000


@pytest.mark.parametrize("credits", [0, 31, -5, 100])
def test_tuition_out_of_range(credits: int) -> None:
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)
