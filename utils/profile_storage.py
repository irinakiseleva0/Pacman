from __future__ import annotations

import json

from utils.storage_paths import PROFILE_FILE


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
    },
    "mode_mastery": {
        "Arcade": 0,
        "Endless": 0,
        "Challenge": 0,
        "Time Attack": 0,
    },
    "challenge_credits": 0,
    "challenge_clears": 0,
    "challenge_streak": 0,
    "best_challenge_streak": 0,
    "challenge_rewards": {},
    "run_history": [],
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
            elif key in profile:
                profile[key] = int(value)
    return profile


def save_profile(profile: dict) -> None:
    PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PROFILE_FILE.open("w", encoding="utf-8") as file:
        json.dump(profile, file, ensure_ascii=False, indent=2)
