"""Deterministic tools for credit parsing and tuition calculation.

Step 6: Pure deterministic business logic without external side effects or LLM dependencies.
"""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, ValidationError

from assistant_core.errors import InvalidRequest

__all__ = [
    "parse_credits",
    "tuition",
    "run_tool_call",
]


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from 'fee for 18 credits and 2 retake'."""
    retake = re.search(r"(\d+)\s*retake", text, flags=re.IGNORECASE)
    numbers = [int(n) for n in re.findall(r"\d+", text)]
    retake_n = int(retake.group(1)) if retake else 0
    others = numbers.copy()

    if retake:
        others.remove(retake_n)

    if not others:
        raise InvalidRequest("How many credits?")

    return others[0], retake_n


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    """Calculate total tuition fee deterministically."""
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")

    if retake < 0:
        raise InvalidRequest("Retake credits cannot be negative.")

    return int(credits * rate + retake * rate * retake_multiplier)


# ---------------------------------------------------------------- Lab 6: tool calling
# An LLM may ask for a tool with JSON like {"tool": "calc_fee", "args": {"credits": 18, "retake": 2}}.
# We never trust the arguments: they are validated with a schema, then a deterministic function runs.
class FeeArgs(BaseModel):
    credits: int = Field(ge=1, le=30)
    retake: int = Field(default=0, ge=0, le=30)


TOOL_SPECS = {
    "calc_fee": {
        "description": "Compute tuition in VND for a number of credits and retake credits.",
        "parameters": FeeArgs.model_json_schema(),
    },
}


def run_tool_call(raw: str, rate: int, retake_multiplier: float, max_credits: int) -> str | None:
    """Return the tool result as text, or None if `raw` is not a tool call. Raises InvalidRequest on bad args."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "tool" not in data:
        return None
    if data["tool"] != "calc_fee":
        raise InvalidRequest(f"unknown tool {data['tool']!r}")
    try:
        args = FeeArgs.model_validate(data.get("args", {}))
    except ValidationError as exc:
        raise InvalidRequest("invalid tool arguments") from exc
    total = tuition(args.credits, args.retake, rate, retake_multiplier, max_credits)
    return f"Your tuition is {total:,} VND."
