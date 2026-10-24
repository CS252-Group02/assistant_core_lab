"""Deterministic tools for credit parsing and tuition calculation.

Step 6: Pure deterministic business logic without external side effects or LLM dependencies.
"""

from __future__ import annotations

import re

from assistant_core.errors import InvalidRequest

__all__ = [
    "parse_credits",
    "tuition",
]


def parse_credits(text: str) -> tuple[int, int]:
    """Parse regular credits and retake credits from input text.

    Args:
        text: The user input message.

    Returns:
        tuple[int, int]: A tuple containing (credits, retake_credits).

    Raises:
        InvalidRequest: If regular credits cannot be identified.
    """
    retake_match = re.search(r"(\d+)\s*retake", text, flags=re.IGNORECASE)
    numbers = [int(n) for n in re.findall(r"\d+", text)]
    retake_credits = int(retake_match.group(1)) if retake_match else 0
    remaining_numbers = numbers.copy()

    if retake_match:
        remaining_numbers.remove(retake_credits)

    if not remaining_numbers:
        raise InvalidRequest("How many credits?")

    return remaining_numbers[0], retake_credits


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    """Calculate total tuition fee deterministically.

    Args:
        credits: Number of regular enrolled credits.
        retake: Number of retake credits.
        rate: Cost per credit in VND.
        retake_multiplier: Multiplier applied to retake credits.
        max_credits: Upper limit of credits allowed per regular semester.

    Returns:
        int: Total tuition in VND.

    Raises:
        InvalidRequest: If credits are not within allowable range [1, max_credits].
    """
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")

    return int(credits * rate + retake * rate * retake_multiplier)
