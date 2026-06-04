from __future__ import annotations

from utils.storage_paths import LEGACY_SCORE_FILE, SCORE_FILE, atomic_write_json, migrate_legacy_file, read_json


def load_high_score() -> int:
    migrate_legacy_file(SCORE_FILE, LEGACY_SCORE_FILE)
    data = read_json(SCORE_FILE)
    if isinstance(data, dict):
        try:
            return int(data.get("high_score", 0))
        except (TypeError, ValueError):
            return 0
    return 0


def save_high_score(score: int) -> None:
    data = {"high_score": score}
    atomic_write_json(SCORE_FILE, data)
