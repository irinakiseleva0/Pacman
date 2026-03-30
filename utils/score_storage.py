from __future__ import annotations

import json

from utils.storage_paths import LEGACY_SCORE_FILE, SCORE_FILE, atomic_write_json, migrate_legacy_file


def load_high_score() -> int:
    migrate_legacy_file(SCORE_FILE, LEGACY_SCORE_FILE)
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
    atomic_write_json(SCORE_FILE, data)
