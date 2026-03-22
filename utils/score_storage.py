from __future__ import annotations

import json
from pathlib import Path


SCORE_FILE = Path("scores.json")


def load_high_score() -> int:
    if not SCORE_FILE.exists():
        return 0

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return int(data.get("high_score", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        return 0


def save_high_score(score: int) -> None:
    data = {"high_score": score}

    with open(SCORE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)