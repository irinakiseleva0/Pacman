from __future__ import annotations

import json

from utils.storage_paths import LEGACY_PROFILE_FILE, PROFILE_FILE, atomic_write_json, migrate_legacy_file


DEFAULT_PROFILE = {
    "total_runs": 0,
    "total_wins": 0,
    "total_losses": 0,
    "total_levels_cleared": 0,
    "best_score": 0,
    "highest_level": 1,
    "total_dots_eaten": 0,
    "total_power_seeds": 0,
    "total_cherries": 0,
    "total_ghosts_eaten": 0,
    "difficulty_runs": {
        "Easy": 0,
        "Normal": 0,
        "Hard": 0,
    },
    "mode_runs": {
        "Arcade": 0,
        "Endless": 0,
        "Challenge": 0,
        "Time Attack": 0,
        "DailyChallenge": 0,
    },
    "mode_mastery": {
        "Arcade": 0,
        "Endless": 0,
        "Challenge": 0,
        "Time Attack": 0,
        "DailyChallenge": 0,
    },
    "challenge_credits": 0,
    "challenge_clears": 0,
    "challenge_streak": 0,
    "best_challenge_streak": 0,
    "challenge_rewards": {},
    "unlocked_skins": {},
    "style_medals": {
        "No Panic Clear": 0,
        "Predator Run": 0,
        "Close-Call Survivor": 0,
        "Line Master": 0,
    },
    "daily_progress": {
        "date": "",
        "completed": [],
        "streak": 0,
        "last_full_clear_date": "",
        "total_completed_days": 0,
    },
    "series_progress": {
        "clear_streak": 0,
        "best_clear_streak": 0,
        "grade_streak": 0,
        "best_grade_streak": 0,
    },
    "mode_records": {
        "Arcade": {"best_score": 0, "best_grade": "", "wins": 0},
        "Endless": {"best_score": 0, "best_grade": "", "wins": 0},
        "Challenge": {"best_score": 0, "best_grade": "", "wins": 0},
        "Time Attack": {"best_score": 0, "best_grade": "", "wins": 0},
        "DailyChallenge": {"best_score": 0, "best_grade": "", "wins": 0},
    },
    "district_records": {
        "1": {"best_score": 0, "best_grade": "", "clears": 0, "best_mode_scores": {"Arcade": 0, "Endless": 0, "Challenge": 0, "Time Attack": 0, "DailyChallenge": 0}},
        "2": {"best_score": 0, "best_grade": "", "clears": 0, "best_mode_scores": {"Arcade": 0, "Endless": 0, "Challenge": 0, "Time Attack": 0, "DailyChallenge": 0}},
        "3": {"best_score": 0, "best_grade": "", "clears": 0, "best_mode_scores": {"Arcade": 0, "Endless": 0, "Challenge": 0, "Time Attack": 0, "DailyChallenge": 0}},
        "4": {"best_score": 0, "best_grade": "", "clears": 0, "best_mode_scores": {"Arcade": 0, "Endless": 0, "Challenge": 0, "Time Attack": 0, "DailyChallenge": 0}},
        "5": {"best_score": 0, "best_grade": "", "clears": 0, "best_mode_scores": {"Arcade": 0, "Endless": 0, "Challenge": 0, "Time Attack": 0, "DailyChallenge": 0}},
    },
    "run_history": [],
    "last_seed": 0,
    "daily_challenge_last_date": "",
    "settings": {
        "fx_intensity": "High",
        "screen_flash": 1,
        "screen_shake": 1,
        "music_enabled": 1,
        "sfx_enabled": 1,
        "tutorial_enabled": 1,
        "capture_mode": 0,
        "theme_name": "Neon District",
        "hud_pack_name": "Standard",
        "title_variant_name": "Standard",
    },
    "tutorial_seen": 0,
}


def load_profile() -> dict:
    migrate_legacy_file(PROFILE_FILE, LEGACY_PROFILE_FILE)
    try:
        with PROFILE_FILE.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    except (OSError, ValueError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULT_PROFILE))

    profile = json.loads(json.dumps(DEFAULT_PROFILE))
    if isinstance(raw, dict):
        for key, value in raw.items():
            if key == "difficulty_runs" and isinstance(value, dict):
                for diff in profile["difficulty_runs"]:
                    profile["difficulty_runs"][diff] = int(value.get(diff, 0))
            elif key == "mode_runs" and isinstance(value, dict):
                for mode in profile["mode_runs"]:
                    profile["mode_runs"][mode] = int(value.get(mode, 0))
            elif key == "mode_mastery" and isinstance(value, dict):
                for mode in profile["mode_mastery"]:
                    profile["mode_mastery"][mode] = int(value.get(mode, 0))
            elif key == "challenge_rewards" and isinstance(value, dict):
                rewards: dict[str, int] = {}
                for reward_name, reward_value in value.items():
                    rewards[str(reward_name)] = 1 if int(reward_value) else 0
                profile["challenge_rewards"] = rewards
            elif key == "unlocked_skins" and isinstance(value, dict):
                skins: dict[str, int] = {}
                for skin_name, skin_value in value.items():
                    skins[str(skin_name)] = 1 if int(skin_value) else 0
                profile["unlocked_skins"] = skins
            elif key == "style_medals" and isinstance(value, dict):
                medals: dict[str, int] = {}
                for medal_name in profile["style_medals"]:
                    medals[medal_name] = max(0, int(value.get(medal_name, 0)))
                profile["style_medals"] = medals
            elif key == "daily_progress" and isinstance(value, dict):
                profile["daily_progress"]["date"] = str(value.get("date", ""))
                completed = value.get("completed", [])
                if isinstance(completed, list):
                    profile["daily_progress"]["completed"] = [str(item) for item in completed[:8]]
                profile["daily_progress"]["streak"] = max(0, int(value.get("streak", 0)))
                profile["daily_progress"]["last_full_clear_date"] = str(value.get("last_full_clear_date", ""))
                profile["daily_progress"]["total_completed_days"] = max(0, int(value.get("total_completed_days", 0)))
            elif key == "series_progress" and isinstance(value, dict):
                for series_key in profile["series_progress"]:
                    profile["series_progress"][series_key] = max(0, int(value.get(series_key, 0)))
            elif key == "mode_records" and isinstance(value, dict):
                records: dict[str, dict] = json.loads(json.dumps(profile["mode_records"]))
                for mode_name in records:
                    record = value.get(mode_name, {})
                    if not isinstance(record, dict):
                        continue
                    records[mode_name]["best_score"] = max(0, int(record.get("best_score", 0)))
                    records[mode_name]["best_grade"] = str(record.get("best_grade", ""))
                    records[mode_name]["wins"] = max(0, int(record.get("wins", 0)))
                profile["mode_records"] = records
            elif key == "district_records" and isinstance(value, dict):
                records: dict[str, dict] = json.loads(json.dumps(profile["district_records"]))
                for map_key in records:
                    record = value.get(map_key, {})
                    if not isinstance(record, dict):
                        continue
                    records[map_key]["best_score"] = max(0, int(record.get("best_score", 0)))
                    records[map_key]["best_grade"] = str(record.get("best_grade", ""))
                    records[map_key]["clears"] = max(0, int(record.get("clears", 0)))
                    mode_scores = record.get("best_mode_scores", {})
                    if isinstance(mode_scores, dict):
                        for mode_name in records[map_key]["best_mode_scores"]:
                            records[map_key]["best_mode_scores"][mode_name] = max(0, int(mode_scores.get(mode_name, 0)))
                profile["district_records"] = records
            elif key == "run_history" and isinstance(value, list):
                history: list[dict] = []
                for item in value[:12]:
                    if not isinstance(item, dict):
                        continue
                    history.append(
                        {
                            "mode": str(item.get("mode", "Arcade")),
                            "challenge": str(item.get("challenge", "")),
                            "difficulty": str(item.get("difficulty", "Normal")),
                            "result": str(item.get("result", "lose")),
                            "score": int(item.get("score", 0)),
                            "level": int(item.get("level", 1)),
                            "grade": str(item.get("grade", "")),
                            "map": int(item.get("map", 1)),
                            "seed": int(item.get("seed", 0)),
                            "medals": [str(medal) for medal in item.get("medals", [])[:4]] if isinstance(item.get("medals", []), list) else [],
                        }
                    )
                profile["run_history"] = history
            elif key == "settings" and isinstance(value, dict):
                profile["settings"]["fx_intensity"] = str(value.get("fx_intensity", "High"))
                profile["settings"]["screen_flash"] = 1 if int(value.get("screen_flash", 1)) else 0
                profile["settings"]["screen_shake"] = 1 if int(value.get("screen_shake", 1)) else 0
                profile["settings"]["music_enabled"] = 1 if int(value.get("music_enabled", 1)) else 0
                profile["settings"]["sfx_enabled"] = 1 if int(value.get("sfx_enabled", 1)) else 0
                profile["settings"]["tutorial_enabled"] = 1 if int(value.get("tutorial_enabled", 1)) else 0
                profile["settings"]["capture_mode"] = 1 if int(value.get("capture_mode", 0)) else 0
                profile["settings"]["theme_name"] = str(value.get("theme_name", "Neon District"))
                profile["settings"]["hud_pack_name"] = str(value.get("hud_pack_name", "Standard"))
                profile["settings"]["title_variant_name"] = str(value.get("title_variant_name", "Standard"))
            elif key == "daily_challenge_last_date":
                profile[key] = str(value)
            elif key in profile:
                profile[key] = int(value)
    return profile


def save_profile(profile: dict) -> None:
    atomic_write_json(PROFILE_FILE, profile)
