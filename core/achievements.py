from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Achievement:
    key: str
    title: str
    detail: str
    check: Callable[[object], bool]


def _profile_value(ctx, key: str, default: int = 0) -> int:
    return int(getattr(ctx, "profile", {}).get(key, default))


def _mode_runs(ctx, mode: str) -> int:
    return int(getattr(ctx, "profile", {}).get("mode_runs", {}).get(mode, 0))


def _level_stat(ctx, key: str) -> int:
    stats = getattr(ctx, "run_stats", None)
    if stats is None:
        return 0
    start_names = {
        "dots_eaten": "level_start_dots",
        "power_seeds_eaten": "level_start_power_seeds",
        "cherries_eaten": "level_start_cherries",
        "ghosts_eaten": "level_start_ghosts",
    }
    start_key = start_names.get(key, f"level_start_{key}")
    return max(0, int(getattr(stats, key, 0)) - int(getattr(stats, start_key, 0)))


ACHIEVEMENTS: tuple[Achievement, ...] = (
    Achievement("first_credit", "First Credit", "Start your first run", lambda ctx: _profile_value(ctx, "total_runs") >= 1),
    Achievement("first_blood", "First Blood", "Eat your first ghost", lambda ctx: getattr(ctx.run_stats, "ghosts_eaten", 0) >= 1 or _profile_value(ctx, "total_ghosts_eaten") >= 1),
    Achievement("ghost_buster", "Ghost Buster", "Eat 4 ghosts from one power seed", lambda ctx: int(getattr(ctx, "ghost_combo", 0)) >= 4),
    Achievement("speed_run", "Speed Run", "Clear a level in under 30 seconds", lambda ctx: getattr(ctx.run_stats, "levels_cleared", 0) >= 1 and getattr(ctx.run_stats, "level_elapsed_seconds", 999.0) < 30.0),
    Achievement("pacifist", "Pacifist", "Clear a level without eating ghosts", lambda ctx: getattr(ctx.run_stats, "levels_cleared", 0) >= 1 and _level_stat(ctx, "ghosts_eaten") == 0),
    Achievement("street_sweeper", "Street Sweeper", "Eat 250 dots", lambda ctx: _profile_value(ctx, "total_dots_eaten") + getattr(ctx.run_stats, "dots_eaten", 0) >= 250),
    Achievement("overcharged", "Overcharged", "Trigger 25 power seeds", lambda ctx: _profile_value(ctx, "total_power_seeds") + getattr(ctx.run_stats, "power_seeds_eaten", 0) >= 25),
    Achievement("cherry_picker", "Cherry Picker", "Collect 10 cherries", lambda ctx: _profile_value(ctx, "total_cherries") + getattr(ctx.run_stats, "cherries_eaten", 0) >= 10),
    Achievement("district_clear", "District Clear", "Clear your first level", lambda ctx: _profile_value(ctx, "total_levels_cleared") >= 1),
    Achievement("hi_score", "Hi-Score", "Reach 5000 points", lambda ctx: max(_profile_value(ctx, "best_score"), int(getattr(ctx, "score", 0))) >= 5000),
    Achievement("arcade_winner", "Arcade Winner", "Win one full run", lambda ctx: _profile_value(ctx, "total_wins") >= 1),
    Achievement("endless_mindset", "Endless Mindset", "Start 3 Endless runs", lambda ctx: _mode_runs(ctx, "Endless") >= 3),
    Achievement("trial_board", "Trial Board", "Start 5 Challenge runs", lambda ctx: _mode_runs(ctx, "Challenge") >= 5),
    Achievement("close_call", "Close-Call Survivor", "Log 4 near misses in one run", lambda ctx: getattr(ctx.run_stats, "near_misses", 0) >= 4),
    Achievement("line_master", "Line Master", "Score 3 line bonuses in one run", lambda ctx: getattr(ctx.run_stats, "line_bonuses", 0) >= 3),
)


class AchievementManager:
    def __init__(self, achievements: tuple[Achievement, ...] = ACHIEVEMENTS) -> None:
        self.achievements = achievements

    def normalize_profile(self, profile: dict) -> None:
        stored = profile.get("achievements", {})
        if not isinstance(stored, dict):
            stored = {}
        profile["achievements"] = {str(key): 1 if int(value) else 0 for key, value in stored.items()}

    def check_all(self, game_state) -> list[Achievement]:
        profile = getattr(game_state, "profile", {})
        self.normalize_profile(profile)
        unlocked: list[Achievement] = []
        for achievement in self.achievements:
            if int(profile["achievements"].get(achievement.key, 0)):
                continue
            if achievement.check(game_state):
                profile["achievements"][achievement.key] = 1
                unlocked.append(achievement)
        return unlocked

    def entries(self, game_state) -> list[tuple[str, str, bool]]:
        profile = getattr(game_state, "profile", {})
        self.normalize_profile(profile)
        return [
            (
                achievement.title,
                achievement.detail,
                bool(int(profile["achievements"].get(achievement.key, 0))),
            )
            for achievement in self.achievements
        ]
