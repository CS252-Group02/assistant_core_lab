from ui.logic import format_sources


def test_format_sources_empty():
    assert format_sources([]) == ""


def test_format_sources_single():
    assert format_sources([{"id": "H26#5.3", "title": "5.3 Thesis registration"}]) == (
        "Sources: H26#5.3 — 5.3 Thesis registration"
    )


def test_format_sources_multiple_in_api_order():
    sources = [
        {"id": "S26#1", "title": "1 Library borrowing"},
        {"id": "H26#5.3", "title": "5.3 Thesis registration"},
    ]
    assert format_sources(sources) == (
        "Sources: S26#1 — 1 Library borrowing; H26#5.3 — 5.3 Thesis registration"
    )
