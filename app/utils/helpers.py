from typing import List


def parse_ingredients(raw_input: str) -> List[str]:
    """
    Converts comma-separated ingredient string
    into a clean list.
    """

    return [
        ing.strip().lower()
        for ing in raw_input.split(",")
        if ing.strip()
    ]


def safe_float(value, default: float = 0.0) -> float:
    """
    Safely converts value to float.
    """

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def percentage(value: float) -> int:
    """
    Converts decimal to percentage integer.
    """

    return int(round(value * 100))
