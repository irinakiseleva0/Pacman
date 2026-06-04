from __future__ import annotations

from utils.storage_paths import DAILY_SCORE_FILE, LEGACY_DAILY_SCORE_FILE, atomic_write_json, migrate_legacy_file, read_json


def load_daily_scores() -> dict:
    migrate_legacy_file(DAILY_SCORE_FILE, LEGACY_DAILY_SCORE_FILE)
    data = read_json(DAILY_SCORE_FILE)
    if data is None:
        return {"scores": []}

    scores = data.get("scores", []) if isinstance(data, dict) else []
    if not isinstance(scores, list):
        return {"scores": []}
    return {
        "scores": [
            {
                "date": str(item.get("date", "")),
                "seed": int(item.get("seed", 0)),
                "score": int(item.get("score", 0)),
                "grade": str(item.get("grade", "")),
                "result": str(item.get("result", "")),
            }
            for item in scores
            if isinstance(item, dict)
        ][:30]
    }


def save_daily_scores(data: dict) -> None:
    atomic_write_json(DAILY_SCORE_FILE, data)


def record_daily_score(date_key: str, seed: int, score: int, grade: str, result: str) -> None:
    data = load_daily_scores()
    entries = [entry for entry in data["scores"] if entry.get("date") != date_key]
    entries.insert(
        0,
        {
            "date": date_key,
            "seed": int(seed),
            "score": int(score),
            "grade": str(grade),
            "result": str(result),
        },
    )
    data["scores"] = entries[:30]
    save_daily_scores(data)
