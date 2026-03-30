from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from raylib import colors

from core.balance import Config, DIFFICULTY_PRESETS, DifficultyPreset
from core.game_data import (
    ACHIEVEMENT_DEFS,
    ARCADE_CHAPTERS,
    CHALLENGE_PRESETS,
    CHALLENGE_TRACK_THRESHOLDS,
    DISTRICT_MODIFIERS,
    ENDLESS_TIERS,
    GAME_MODE_PRESETS,
    HUD_PACK_PRESETS,
    MAP_TRAITS,
    MODE_MASTERY_THRESHOLDS,
    RANK_THRESHOLDS,
    THEME_PRESETS,
    TITLE_VARIANT_PRESETS,
    ChallengePreset,
    DistrictModifier,
    GameModePreset,
    HudPackPreset,
    MapTrait,
    RunDirective,
    ThemePreset,
    TitleVariantPreset,
)
from core.services import ProfileService, ProgressionService, SettingsService
from core.state import RunState, RunStats, RuntimeRefs, VisualSystems
from ui.layout import DEFAULT_LAYOUT, LAYOUT_PROFILES
from utils.profile_storage import PROFILE_FILE

@dataclass
class GameContext:
    cfg: Config = field(default_factory=Config)
    run: RunState = field(default_factory=RunState)
    visual: VisualSystems = field(default_factory=VisualSystems)
    runtime: RuntimeRefs = field(default_factory=RuntimeRefs)
    profile_service: ProfileService = field(default_factory=ProfileService)
    progression_service: ProgressionService = field(default_factory=ProgressionService)
    settings: SettingsService = field(init=False)

    def __post_init__(self):
        self.settings = SettingsService(self.profile_service)
        self.apply_layout(self.cfg.layout_name)
        self.set_capture_mode_enabled(self.capture_mode_enabled(), save=False)
        # Initialize lives from config if not already set
        if self.lives == 3:
            self.lives = self.cfg.initial_lives

    @property
    def difficulty(self) -> str:
        return self.run.difficulty

    @difficulty.setter
    def difficulty(self, value: str) -> None:
        self.run.difficulty = value

    @property
    def game_mode(self) -> str:
        return self.run.game_mode

    @game_mode.setter
    def game_mode(self, value: str) -> None:
        self.run.game_mode = value

    @property
    def challenge_name(self) -> str:
        return self.run.challenge_name

    @challenge_name.setter
    def challenge_name(self, value: str) -> None:
        self.run.challenge_name = value

    @property
    def score(self) -> int:
        return self.run.score

    @score.setter
    def score(self, value: int) -> None:
        self.run.score = value

    @property
    def high_score(self) -> int:
        return self.run.high_score

    @high_score.setter
    def high_score(self, value: int) -> None:
        self.run.high_score = value

    @property
    def lives(self) -> int:
        return self.run.lives

    @lives.setter
    def lives(self, value: int) -> None:
        self.run.lives = value

    @property
    def current_level(self) -> int:
        return self.run.current_level

    @current_level.setter
    def current_level(self, value: int) -> None:
        self.run.current_level = value

    @property
    def last_result(self) -> str:
        return self.run.last_result

    @last_result.setter
    def last_result(self, value: str) -> None:
        self.run.last_result = value

    @property
    def should_resume_game(self) -> bool:
        return self.run.should_resume_game

    @should_resume_game.setter
    def should_resume_game(self, value: bool) -> None:
        self.run.should_resume_game = value

    @property
    def ghost_mode(self) -> str:
        return self.run.ghost_mode

    @ghost_mode.setter
    def ghost_mode(self, value: str) -> None:
        self.run.ghost_mode = value

    @property
    def ghost_mode_timer(self) -> int:
        return self.run.ghost_mode_timer

    @ghost_mode_timer.setter
    def ghost_mode_timer(self, value: int) -> None:
        self.run.ghost_mode_timer = value

    @property
    def ghost_combo(self) -> int:
        return self.run.ghost_combo

    @ghost_combo.setter
    def ghost_combo(self, value: int) -> None:
        self.run.ghost_combo = value

    @property
    def power_chain_level(self) -> int:
        return self.run.power_chain_level

    @power_chain_level.setter
    def power_chain_level(self, value: int) -> None:
        self.run.power_chain_level = value

    @property
    def power_chain_window(self) -> int:
        return self.run.power_chain_window

    @power_chain_window.setter
    def power_chain_window(self, value: int) -> None:
        self.run.power_chain_window = value

    @property
    def route_chain_count(self) -> int:
        return self.run.route_chain_count

    @route_chain_count.setter
    def route_chain_count(self, value: int) -> None:
        self.run.route_chain_count = value

    @property
    def route_chain_window(self) -> int:
        return self.run.route_chain_window

    @route_chain_window.setter
    def route_chain_window(self, value: int) -> None:
        self.run.route_chain_window = value

    @property
    def pressure_stage(self) -> int:
        return self.run.pressure_stage

    @pressure_stage.setter
    def pressure_stage(self, value: int) -> None:
        self.run.pressure_stage = value

    @property
    def time_attack_seconds(self) -> float:
        return self.run.time_attack_seconds

    @time_attack_seconds.setter
    def time_attack_seconds(self, value: float) -> None:
        self.run.time_attack_seconds = value

    @property
    def particles(self):
        return self.visual.particles

    @property
    def screen_shake(self):
        return self.visual.screen_shake

    @property
    def floating_text(self):
        return self.visual.floating_text

    @property
    def screen_flash(self):
        return self.visual.screen_flash

    @property
    def visual_time(self) -> float:
        return self.visual.visual_time

    @visual_time.setter
    def visual_time(self, value: float) -> None:
        self.visual.visual_time = value

    @property
    def pacman(self):
        return self.runtime.pacman

    @pacman.setter
    def pacman(self, value) -> None:
        self.runtime.pacman = value

    @property
    def game_map(self):
        return self.runtime.game_map

    @game_map.setter
    def game_map(self, value) -> None:
        self.runtime.game_map = value

    @property
    def audio_manager(self):
        return self.runtime.audio_manager

    @audio_manager.setter
    def audio_manager(self, value) -> None:
        self.runtime.audio_manager = value

    @property
    def profile(self) -> dict:
        return self.profile_service.profile

    @profile.setter
    def profile(self, value: dict) -> None:
        self.profile_service.profile = value

    @property
    def run_stats(self) -> RunStats:
        return self.progression_service.run_stats

    @run_stats.setter
    def run_stats(self, value: RunStats) -> None:
        self.progression_service.run_stats = value

    @property
    def pre_run_unlock_snapshot(self) -> dict:
        return self.progression_service.pre_run_unlock_snapshot

    @pre_run_unlock_snapshot.setter
    def pre_run_unlock_snapshot(self, value: dict) -> None:
        self.progression_service.pre_run_unlock_snapshot = value

    @property
    def last_unlock_lines(self) -> tuple[str, str, str]:
        return self.progression_service.last_unlock_lines

    @last_unlock_lines.setter
    def last_unlock_lines(self, value: tuple[str, str, str]) -> None:
        self.progression_service.last_unlock_lines = value

    @property
    def last_unlocks_are_new(self) -> bool:
        return self.progression_service.last_unlocks_are_new

    @last_unlocks_are_new.setter
    def last_unlocks_are_new(self, value: bool) -> None:
        self.progression_service.last_unlocks_are_new = value

    def apply_layout(self, layout_name: str) -> None:
        profile = LAYOUT_PROFILES[layout_name]
        self.cfg.layout_name = profile.name
        self.cfg.tile_size = profile.tile_size
        self.cfg.hud_mode = profile.hud_mode
        self.cfg.hud_extent = profile.hud_extent
        self.cfg.menu_button_width = profile.menu_button_width
        self.cfg.menu_button_height = profile.menu_button_height
        self.cfg.menu_title_size = profile.menu_title_size
        self.cfg.menu_heading_size = profile.menu_heading_size
        self.cfg.menu_body_size = profile.menu_body_size
        self.cfg.menu_footer_size = profile.menu_footer_size
        self.cfg.hud_font_size = profile.hud_font_size
        self.cfg.hud_line_height = profile.hud_line_height
        self.cfg.hud_columns = profile.hud_columns
        self.screen_flash.set_size(self.cfg.window_width, self.cfg.window_height)

    def reset_run_state(self) -> None:
        """Reset progress for a fresh run without touching persistent data."""
        self.score = 0
        self.lives = self.starting_lives()
        self.current_level = 1
        self.last_result = ""
        self.last_unlock_lines = ("", "", "")
        self.last_unlocks_are_new = False
        self.should_resume_game = False
        self.reset_ghost_mode_cycle()
        self.reset_ghost_combo()
        self.pacman = None
        self.game_map = None
        self.run_stats = RunStats()
        self.reset_power_chain()
        self.reset_route_chain()
        self.time_attack_seconds = self.starting_time_attack_seconds()
        self.mark_level_baseline()

    def play_transition_effect(
        self,
        flash_color=colors.WHITE,
        flash_intensity: float = 0.0,
        flash_duration: float = 0.0,
        shake_intensity: float = 0.0,
        shake_duration: float = 0.0,
    ) -> None:
        if flash_intensity > 0 and flash_duration > 0:
            self.trigger_screen_flash(flash_color, flash_intensity, flash_duration)
        if shake_intensity > 0 and shake_duration > 0:
            self.trigger_screen_shake(shake_intensity, shake_duration)

    def start_new_game(self) -> None:
        """Start a new game using the current config."""
        self.pre_run_unlock_snapshot = self.unlock_snapshot()
        self.reset_run_state()
        self.profile["total_runs"] += 1
        self.profile["difficulty_runs"][self.difficulty] += 1
        self.profile["mode_runs"][self.game_mode] += 1
        self.mark_level_baseline()
        self.save_profile()

    def set_game_mode(self, game_mode: str) -> None:
        if game_mode in GAME_MODE_PRESETS:
            self.game_mode = game_mode

    def set_challenge(self, challenge_name: str) -> None:
        if challenge_name in CHALLENGE_PRESETS:
            self.challenge_name = challenge_name

    def challenge_preset(self, challenge_name: Optional[str] = None) -> ChallengePreset:
        return CHALLENGE_PRESETS[challenge_name or self.challenge_name]

    def challenge_summary_lines(self, challenge_name: Optional[str] = None) -> tuple[str, str, str]:
        return self.challenge_preset(challenge_name).summary_lines

    def challenge_unlocked(self, challenge_name: Optional[str] = None) -> bool:
        name = challenge_name or self.challenge_name
        profile = self.profile
        if name == "One Life District":
            return True
        if name == "Score Rush":
            return profile["total_runs"] >= 3
        if name == "Ghost Hunt":
            return profile["total_ghosts_eaten"] >= 10
        if name == "Neon Sprint":
            return profile["highest_level"] >= 2
        if name == "Phantom Debt":
            return profile["total_wins"] >= 1
        if name == "District Ace":
            return profile["best_score"] >= 3500
        if name == "Midnight Relay":
            return profile["total_levels_cleared"] >= 1
        if name == "Credit Burner":
            return profile["best_score"] >= 2000
        if name == "Last Call":
            return profile["total_ghosts_eaten"] >= 20
        if name == "Redline Protocol":
            return int(self.profile.get("challenge_credits", 0)) >= 18
        if name == "Clock Reaper":
            return self.mode_mastery_value("Time Attack") >= 9
        return False

    def challenge_entries(self) -> list[tuple[str, ChallengePreset, bool]]:
        return [
            (name, preset, self.challenge_unlocked(name))
            for name, preset in CHALLENGE_PRESETS.items()
        ]

    def challenge_board_summary_lines(self) -> tuple[str, str, str]:
        entries = self.challenge_entries()
        unlocked = sum(1 for _name, _preset, is_open in entries if is_open)
        cleared = self.challenge_reward_count()
        return (
            f"Unlocked {unlocked}/{len(entries)}",
            f"Cleared {cleared}/{len(entries)}",
            f"Rank {self.challenge_track_rank()}",
        )

    def challenge_reward_unlocked(self, challenge_name: Optional[str] = None) -> bool:
        name = challenge_name or self.challenge_name
        rewards = self.profile.get("challenge_rewards", {})
        return bool(int(rewards.get(name, 0)))

    def challenge_reward_count(self) -> int:
        rewards = self.profile.get("challenge_rewards", {})
        return sum(1 for _name, value in rewards.items() if int(value))

    def challenge_credit_reward(self, result: str) -> int:
        if self.game_mode != "Challenge":
            return 0
        if result == "game_won":
            return 3
        if result == "challenge_failed":
            return 1
        return 0

    def challenge_track_rank(self) -> str:
        credits = int(self.profile.get("challenge_credits", 0))
        if credits >= 30:
            return "TRIAL MASTER"
        if credits >= 18:
            return "HUNTER"
        if credits >= 9:
            return "RUNNER"
        if credits >= 3:
            return "SCOUT"
        return "UNRANKED"

    def next_challenge_rank_goal(self) -> Optional[str]:
        credits = int(self.profile.get("challenge_credits", 0))
        for threshold, title in CHALLENGE_TRACK_THRESHOLDS:
            if credits < threshold:
                return f"{title} at {threshold}C  ({threshold - credits} to go)"
        return None

    def challenge_progress_lines(self) -> tuple[str, str, str]:
        credits = int(self.profile.get("challenge_credits", 0))
        streak = int(self.profile.get("challenge_streak", 0))
        best_streak = int(self.profile.get("best_challenge_streak", 0))
        return (
            f"Credits {credits}  Rank {self.challenge_track_rank()}",
            f"Clears {int(self.profile.get('challenge_clears', 0))}  Streak {streak}",
            f"Best Streak {best_streak}",
        )

    def mark_level_baseline(self) -> None:
        self.run_stats.level_start_score = self.score
        self.run_stats.level_start_dots = self.run_stats.dots_eaten
        self.run_stats.level_start_power_seeds = self.run_stats.power_seeds_eaten
        self.run_stats.level_start_cherries = self.run_stats.cherries_eaten
        self.run_stats.level_start_ghosts = self.run_stats.ghosts_eaten

    def level_progress_snapshot(self) -> dict[str, int]:
        return {
            "score": max(0, self.score - self.run_stats.level_start_score),
            "dots": max(0, self.run_stats.dots_eaten - self.run_stats.level_start_dots),
            "power_seeds": max(0, self.run_stats.power_seeds_eaten - self.run_stats.level_start_power_seeds),
            "cherries": max(0, self.run_stats.cherries_eaten - self.run_stats.level_start_cherries),
            "ghosts": max(0, self.run_stats.ghosts_eaten - self.run_stats.level_start_ghosts),
        }

    def current_run_directive(self) -> RunDirective:
        if self.game_mode == "Arcade":
            if self.mode_mastery_value("Arcade") >= 18:
                if self.current_level == 1:
                    return RunDirective("CAMPAIGN EX", "earn 1600 score", "score", 1600, 420, colors.SKYBLUE)
                if self.current_level == 2:
                    return RunDirective("MARKET CUT", "eat 3 ghosts", "ghosts", 3, 640, colors.GOLD)
                return RunDirective("FINAL PUSH", "collect 1 cherry", "cherries", 1, 760, colors.RED)
            if self.current_level == 1:
                return RunDirective("CLEAN SWEEP", "eat 2 power seeds", "power_seeds", 2, 300, colors.MAGENTA)
            if self.current_level == 2:
                return RunDirective("NIGHT MARKET", "collect 1 cherry", "cherries", 1, 450, colors.GOLD)
            return RunDirective("GHOST BREAK", "eat 3 ghosts", "ghosts", 3, 700, colors.RED)

        if self.game_mode == "Endless":
            if self.mode_mastery_value("Endless") >= 18:
                cycle = self.current_level % 3
                if cycle == 1:
                    return RunDirective("OVERCLOCK", "earn 2200 score", "score", 2200 + max(0, self.current_level - 1) * 140, 520, colors.ORANGE)
                if cycle == 2:
                    return RunDirective("HUNTER LOOP", "eat 5 ghosts", "ghosts", 5, 760, colors.RED)
                return RunDirective("BONUS MARKET", "collect 2 cherries", "cherries", 2, 680, colors.GOLD)
            cycle = self.current_level % 3
            if cycle == 1:
                return RunDirective("HARVEST RUN", "earn 1800 score", "score", 1800 + max(0, self.current_level - 1) * 120, 400, colors.GOLD)
            if cycle == 2:
                return RunDirective("VOLTAGE CHAIN", "eat 4 ghosts", "ghosts", 4, 650, colors.SKYBLUE)
            return RunDirective("LUCK RUSH", "collect 1 cherry", "cherries", 1, 500, colors.GREEN)

        if self.game_mode == "Time Attack":
            if self.mode_mastery_value("Time Attack") >= 9:
                if self.current_level == 1:
                    return RunDirective("SPLIT PUSH", "finish above 1700", "score", 1700, 520, colors.ORANGE)
                if self.current_level == 2:
                    return RunDirective("CLOCK HUNT", "eat 4 ghosts", "ghosts", 4, 720, colors.RED)
                return RunDirective("ZERO HOUR", "collect 1 cherry", "cherries", 1, 820, colors.GOLD)
            if self.current_level == 1:
                return RunDirective("FAST LINE", "finish above 1400", "score", 1400, 450, colors.ORANGE)
            if self.current_level == 2:
                return RunDirective("CUT ROUTE", "eat 3 ghosts", "ghosts", 3, 650, colors.SKYBLUE)
            return RunDirective("FINAL LAP", "collect 1 cherry", "cherries", 1, 700, colors.GOLD)

        preset = self.challenge_preset()
        if preset.target_score > 0:
            return RunDirective("PRESTIGE SCORE", f"finish above {preset.target_score}", "score", preset.target_score, 800, preset.accent)
        if preset.target_ghosts > 0:
            return RunDirective("HUNTER QUOTA", f"eat {preset.target_ghosts} ghosts", "ghosts", preset.target_ghosts, 800, preset.accent)
        return RunDirective("LAST LIFE CLEAR", "survive the district", "clear", 1, 600, preset.accent)

    def directive_progress_text(self) -> str:
        directive = self.current_run_directive()
        if directive.kind == "clear":
            return f"clear alive +{directive.bonus_score}"
        progress = self.level_progress_snapshot().get(directive.kind, 0)
        if progress >= directive.target_value:
            return f"ready +{directive.bonus_score}"
        return f"{progress}/{directive.target_value}"

    def directive_completed(self) -> bool:
        directive = self.current_run_directive()
        if directive.kind == "clear":
            return self.lives > 0
        progress = self.level_progress_snapshot().get(directive.kind, 0)
        return progress >= directive.target_value

    def directive_clear_bonus(self) -> int:
        if not self.directive_completed():
            return 0
        return self.current_run_directive().bonus_score

    def challenge_reward_lines(self) -> tuple[str, str, str]:
        rewards = [
            preset.reward_title
            for name, preset in CHALLENGE_PRESETS.items()
            if self.challenge_reward_unlocked(name)
        ]
        if not rewards:
            return (
                "No challenge trophies earned yet",
                "Clear challenge trials to unlock badges",
                "The board tracks your prestige clears",
            )
        preview = rewards[:3]
        while len(preview) < 3:
            preview.append("...")
        return (preview[0], preview[1], preview[2])

    def theme_name(self) -> str:
        name = self.settings.get_string("theme_name", "Neon District")
        if name not in THEME_PRESETS:
            return "Neon District"
        return name

    def set_theme_name(self, name: str) -> None:
        if name not in THEME_PRESETS or not self.theme_unlocked(name):
            return
        self.settings.set_string("theme_name", name)

    def hud_pack_name(self) -> str:
        name = self.settings.get_string("hud_pack_name", "Standard")
        if name not in HUD_PACK_PRESETS:
            return "Standard"
        if not self.hud_pack_unlocked(name):
            return "Standard"
        return name

    def set_hud_pack_name(self, name: str) -> None:
        if name not in HUD_PACK_PRESETS or not self.hud_pack_unlocked(name):
            return
        self.settings.set_string("hud_pack_name", name)

    def hud_pack_unlocked(self, name: str) -> bool:
        if name == "Standard":
            return True
        if name == "Relay Grid":
            return self.mode_mastery_value("Arcade") >= 9
        if name == "Hunter Scope":
            return self.challenge_reward_count() >= 4
        if name == "Chrome Vector":
            return self.profile["best_score"] >= 6500
        return False

    def hud_pack_entries(self) -> list[tuple[str, HudPackPreset, bool]]:
        return [(name, preset, self.hud_pack_unlocked(name)) for name, preset in HUD_PACK_PRESETS.items()]

    def next_hud_pack_goal(self) -> Optional[str]:
        for name, _preset, unlocked in self.hud_pack_entries():
            if unlocked:
                continue
            if name == "Relay Grid":
                remaining = max(0, 9 - self.mode_mastery_value("Arcade"))
                return f"{name}: gain {remaining} Arcade mastery"
            if name == "Hunter Scope":
                remaining = max(0, 4 - self.challenge_reward_count())
                return f"{name}: earn {remaining} more trophies"
            if name == "Chrome Vector":
                remaining = max(0, 6500 - int(self.profile["best_score"]))
                return f"{name}: score {remaining} more best-score pts"
        return None

    def reward_progress_lines(self) -> tuple[str, str, str]:
        themes_open = sum(1 for _name, _preset, unlocked in self.theme_entries() if unlocked)
        hud_open = sum(1 for _name, _preset, unlocked in self.hud_pack_entries() if unlocked)
        title_open = sum(1 for _name, _preset, unlocked in self.title_variant_entries() if unlocked)
        return (
            f"Themes {themes_open}/{len(THEME_PRESETS)}  HUD {hud_open}/{len(HUD_PACK_PRESETS)}",
            f"Titles {title_open}/{len(TITLE_VARIANT_PRESETS)}  Trials {self.challenge_reward_count()}/{len(CHALLENGE_PRESETS)}",
            f"Directive Packs {len(self.directive_pack_names())}  Elite Districts {len(self.elite_district_names())}",
        )

    def next_unlock_spotlight_lines(self) -> tuple[str, str, str]:
        goals = [
            self.next_theme_goal(),
            self.next_hud_pack_goal(),
            self.next_title_variant_goal(),
            self.next_directive_pack_goal(),
            self.next_elite_district_goal(),
            self.next_challenge_unlock_goal(),
        ]
        lines = [goal for goal in goals if goal]
        if not lines:
            return (
                "Reward board fully lit",
                "All visible unlock tracks are open",
                "Push mastery and score for prestige",
            )
        while len(lines) < 3:
            lines.append("Complete another run to push unlock progress")
        return (lines[0], lines[1], lines[2])

    def title_variant_name(self) -> str:
        name = self.settings.get_string("title_variant_name", "Standard")
        if name not in TITLE_VARIANT_PRESETS or not self.title_variant_unlocked(name):
            return "Standard"
        return name

    def set_title_variant_name(self, name: str) -> None:
        if name not in TITLE_VARIANT_PRESETS or not self.title_variant_unlocked(name):
            return
        self.settings.set_string("title_variant_name", name)

    def title_variant_unlocked(self, name: str) -> bool:
        if name == "Standard":
            return True
        if name == "Broadcast":
            return int(self.profile.get("total_wins", 0)) >= 2
        if name == "Splitline":
            return self.mode_mastery_value("Time Attack") >= 9
        if name == "Executive":
            return int(self.profile.get("best_score", 0)) >= 7000
        return False

    def title_variant_entries(self) -> list[tuple[str, TitleVariantPreset, bool]]:
        return [(name, preset, self.title_variant_unlocked(name)) for name, preset in TITLE_VARIANT_PRESETS.items()]

    def next_title_variant_goal(self) -> Optional[str]:
        for name, _preset, unlocked in self.title_variant_entries():
            if unlocked:
                continue
            if name == "Broadcast":
                remaining = max(0, 2 - int(self.profile.get("total_wins", 0)))
                return f"{name}: win {remaining} more runs"
            if name == "Splitline":
                remaining = max(0, 9 - self.mode_mastery_value("Time Attack"))
                return f"{name}: gain {remaining} Time Attack mastery"
            if name == "Executive":
                remaining = max(0, 7000 - int(self.profile.get("best_score", 0)))
                return f"{name}: score {remaining} more best-score pts"
        return None

    def directive_pack_names(self) -> set[str]:
        packs = {"Core Directives"}
        if self.mode_mastery_value("Arcade") >= 18:
            packs.add("Campaign EX")
        if self.mode_mastery_value("Endless") >= 18:
            packs.add("Overclock Pack")
        if self.mode_mastery_value("Time Attack") >= 9:
            packs.add("Split-Second Pack")
        return packs

    def next_directive_pack_goal(self) -> Optional[str]:
        if self.mode_mastery_value("Arcade") < 18:
            return f"Campaign EX: gain {18 - self.mode_mastery_value('Arcade')} Arcade mastery"
        if self.mode_mastery_value("Endless") < 18:
            return f"Overclock Pack: gain {18 - self.mode_mastery_value('Endless')} Endless mastery"
        if self.mode_mastery_value("Time Attack") < 9:
            return f"Split-Second Pack: gain {9 - self.mode_mastery_value('Time Attack')} Time Attack mastery"
        return None

    def elite_district_names(self) -> set[str]:
        names = set()
        if self.mode_mastery_value("Endless") >= 12:
            names.add("Redline Sector")
        if int(self.profile.get("best_score", 0)) >= 6000:
            names.add("Null Pulse")
        return names

    def next_elite_district_goal(self) -> Optional[str]:
        if self.mode_mastery_value("Endless") < 12:
            return f"Redline Sector: gain {12 - self.mode_mastery_value('Endless')} Endless mastery"
        if int(self.profile.get("best_score", 0)) < 6000:
            return f"Null Pulse: score {6000 - int(self.profile.get('best_score', 0))} more best-score pts"
        return None

    def theme_unlocked(self, name: str) -> bool:
        if name == "Neon District":
            return True
        if name == "Amber Rain":
            return self.profile["total_wins"] >= 1
        if name == "Ice Circuit":
            return self.challenge_reward_count() >= 2
        if name == "Velvet Alley":
            return self.profile["best_score"] >= 5000
        if name == "Cool Summer":
            return int(self.profile.get("total_levels_cleared", 0)) >= 3
        if name == "Solar Pulse":
            return int(self.profile.get("best_score", 0)) >= 4200
        if name == "Ultraviolet":
            return self.challenge_reward_count() >= 6
        if name == "Grid Echo":
            return self.mode_mastery_value("Arcade") >= 9
        if name == "After Hours":
            return self.mode_mastery_value("Endless") >= 9
        if name == "Trial Chrome":
            return self.mode_mastery_value("Challenge") >= 9
        return False

    def theme_entries(self) -> list[tuple[str, ThemePreset, bool]]:
        return [(name, preset, self.theme_unlocked(name)) for name, preset in THEME_PRESETS.items()]

    def next_theme_goal(self) -> Optional[str]:
        for name, _preset, unlocked in self.theme_entries():
            if unlocked:
                continue
            if name == "Amber Rain":
                remaining = max(0, 1 - int(self.profile["total_wins"]))
                return f"{name}: win {remaining} more run"
            if name == "Ice Circuit":
                remaining = max(0, 2 - self.challenge_reward_count())
                return f"{name}: earn {remaining} more trophies"
            if name == "Velvet Alley":
                remaining = max(0, 5000 - int(self.profile["best_score"]))
                return f"{name}: score {remaining} more best-score pts"
            if name == "Cool Summer":
                remaining = max(0, 3 - int(self.profile.get("total_levels_cleared", 0)))
                return f"{name}: clear {remaining} more levels"
            if name == "Solar Pulse":
                remaining = max(0, 4200 - int(self.profile.get("best_score", 0)))
                return f"{name}: score {remaining} more best-score pts"
            if name == "Ultraviolet":
                remaining = max(0, 6 - self.challenge_reward_count())
                return f"{name}: earn {remaining} more trophies"
            if name == "Grid Echo":
                remaining = max(0, 9 - self.mode_mastery_value("Arcade"))
                return f"{name}: gain {remaining} Arcade mastery"
            if name == "After Hours":
                remaining = max(0, 9 - self.mode_mastery_value("Endless"))
                return f"{name}: gain {remaining} Endless mastery"
            if name == "Trial Chrome":
                remaining = max(0, 9 - self.mode_mastery_value("Challenge"))
                return f"{name}: gain {remaining} Challenge mastery"
        return None

    def effect_palette(self) -> dict[str, object]:
        theme_name = self.theme_name()
        if theme_name == "Amber Rain":
            return {
                "dot": colors.GOLD,
                "power": colors.ORANGE,
                "cherry": (colors.ORANGE, colors.GOLD, colors.YELLOW, colors.RED),
                "respawn": (colors.GOLD, colors.YELLOW, colors.WHITE),
                "ghost": colors.ORANGE,
                "ready_flash": colors.ORANGE,
                "power_flash": colors.GOLD,
                "win_flash": colors.GOLD,
                "death_flash": colors.RED,
            }
        if theme_name == "Ice Circuit":
            return {
                "dot": colors.SKYBLUE,
                "power": colors.WHITE,
                "cherry": (colors.SKYBLUE, colors.WHITE, colors.BLUE, colors.LIGHTGRAY),
                "respawn": (colors.WHITE, colors.SKYBLUE, colors.BLUE),
                "ghost": colors.SKYBLUE,
                "ready_flash": colors.SKYBLUE,
                "power_flash": colors.WHITE,
                "win_flash": colors.SKYBLUE,
                "death_flash": colors.BLUE,
            }
        if theme_name == "Velvet Alley":
            return {
                "dot": colors.MAGENTA,
                "power": colors.VIOLET,
                "cherry": (colors.MAGENTA, colors.PINK, colors.VIOLET, colors.WHITE),
                "respawn": (colors.PINK, colors.VIOLET, colors.WHITE),
                "ghost": colors.VIOLET,
                "ready_flash": colors.MAGENTA,
                "power_flash": colors.VIOLET,
                "win_flash": colors.MAGENTA,
                "death_flash": colors.MAROON,
            }
        if theme_name == "Cool Summer":
            return {
                "dot": colors.SKYBLUE,
                "power": colors.WHITE,
                "cherry": (colors.SKYBLUE, colors.BLUE, colors.VIOLET, colors.WHITE),
                "respawn": (colors.WHITE, colors.SKYBLUE, colors.VIOLET),
                "ghost": colors.BLUE,
                "ready_flash": colors.SKYBLUE,
                "power_flash": colors.WHITE,
                "win_flash": colors.SKYBLUE,
                "death_flash": colors.VIOLET,
            }
        if theme_name == "Solar Pulse":
            return {
                "dot": colors.GOLD,
                "power": colors.YELLOW,
                "cherry": (colors.ORANGE, colors.GOLD, colors.YELLOW, colors.RED),
                "respawn": (colors.GOLD, colors.YELLOW, colors.WHITE),
                "ghost": colors.ORANGE,
                "ready_flash": colors.GOLD,
                "power_flash": colors.YELLOW,
                "win_flash": colors.GOLD,
                "death_flash": colors.RED,
            }
        if theme_name == "Ultraviolet":
            return {
                "dot": colors.VIOLET,
                "power": colors.SKYBLUE,
                "cherry": (colors.VIOLET, colors.BLUE, colors.MAGENTA, colors.WHITE),
                "respawn": (colors.WHITE, colors.VIOLET, colors.SKYBLUE),
                "ghost": colors.MAGENTA,
                "ready_flash": colors.VIOLET,
                "power_flash": colors.SKYBLUE,
                "win_flash": colors.VIOLET,
                "death_flash": colors.MAGENTA,
            }
        if theme_name == "Grid Echo":
            return {
                "dot": colors.SKYBLUE,
                "power": colors.LIME,
                "cherry": (colors.SKYBLUE, colors.LIME, colors.WHITE, colors.GREEN),
                "respawn": (colors.WHITE, colors.SKYBLUE, colors.LIME),
                "ghost": colors.SKYBLUE,
                "ready_flash": colors.SKYBLUE,
                "power_flash": colors.LIME,
                "win_flash": colors.GREEN,
                "death_flash": colors.BLUE,
            }
        if theme_name == "After Hours":
            return {
                "dot": colors.GOLD,
                "power": colors.ORANGE,
                "cherry": (colors.ORANGE, colors.GOLD, colors.RED, colors.PINK),
                "respawn": (colors.GOLD, colors.ORANGE, colors.WHITE),
                "ghost": colors.ORANGE,
                "ready_flash": colors.GOLD,
                "power_flash": colors.ORANGE,
                "win_flash": colors.GOLD,
                "death_flash": colors.MAROON,
            }
        if theme_name == "Trial Chrome":
            return {
                "dot": colors.LIGHTGRAY,
                "power": colors.MAGENTA,
                "cherry": (colors.LIGHTGRAY, colors.WHITE, colors.MAGENTA, colors.VIOLET),
                "respawn": (colors.WHITE, colors.LIGHTGRAY, colors.MAGENTA),
                "ghost": colors.WHITE,
                "ready_flash": colors.LIGHTGRAY,
                "power_flash": colors.MAGENTA,
                "win_flash": colors.WHITE,
                "death_flash": colors.MAGENTA,
            }
        return {
            "dot": colors.YELLOW,
            "power": colors.WHITE,
            "cherry": (colors.RED, colors.PINK, colors.GOLD, colors.ORANGE),
            "respawn": (colors.GOLD, colors.PINK, colors.WHITE),
            "ghost": colors.BLUE,
            "ready_flash": colors.BLUE,
            "power_flash": colors.WHITE,
            "win_flash": colors.GREEN,
            "death_flash": colors.RED,
        }

    def game_mode_preset(self, game_mode: Optional[str] = None) -> GameModePreset:
        return GAME_MODE_PRESETS[game_mode or self.game_mode]

    def mode_summary_lines(self, game_mode: Optional[str] = None) -> tuple[str, str, str]:
        return self.game_mode_preset(game_mode).summary_lines

    def starting_lives(self) -> int:
        if self.game_mode == "Challenge":
            return self.challenge_preset().starting_lives
        return self.cfg.initial_lives

    def starting_time_attack_seconds(self) -> float:
        if self.game_mode != "Time Attack":
            return 0.0
        return 55.0

    def time_attack_clear_bonus_seconds(self) -> float:
        return 18.0

    def time_attack_warning_active(self) -> bool:
        return self.game_mode == "Time Attack" and self.time_attack_seconds <= 12.0

    def mode_score_multiplier(self) -> float:
        if self.game_mode == "Challenge":
            return 1.4
        if self.game_mode == "Time Attack":
            return 1.25
        if self.game_mode == "Endless":
            return min(1.35, 1.1 + max(0, self.current_level - 1) * 0.05)
        return 1.0

    def mode_pressure_bonus(self) -> int:
        if self.game_mode == "Challenge":
            return 2
        if self.game_mode == "Time Attack":
            return 1
        if self.game_mode == "Endless":
            return 1 + min(2, max(0, self.current_level - 1) // 2)
        return 0

    def mode_rage_bonus(self) -> int:
        if self.game_mode == "Challenge":
            return -35
        if self.game_mode == "Endless":
            return -15
        return 25

    def mode_clear_bonus(self) -> int:
        if self.game_mode == "Challenge":
            return 0
        if self.game_mode == "Time Attack":
            return 300 * self.current_level
        if self.game_mode == "Endless":
            return self.endless_tier().clear_bonus * self.current_level // max(1, min(self.current_level, 3))
        return 400 * self.current_level

    def total_levels_for_mode(self, game_mode: Optional[str] = None) -> Optional[int]:
        return self.game_mode_preset(game_mode).max_levels

    def mode_label(self) -> str:
        return self.game_mode_preset().title

    def mode_subtitle(self) -> str:
        if self.game_mode == "Challenge":
            return self.challenge_preset().title
        if self.game_mode == "Endless":
            tier = self.endless_tier()
            return f"{tier.title} | {tier.subtitle}".upper()
        if self.game_mode == "Time Attack":
            return f"CLOCK LIVE | {self.game_mode_preset().subtitle}".upper()
        return self.game_mode_preset().subtitle.upper()

    def endless_tier(self) -> EndlessTier:
        current = ENDLESS_TIERS[0][1]
        for threshold, tier in ENDLESS_TIERS:
            if self.current_level >= threshold:
                current = tier
        return current

    def district_modifier_name(self) -> str:
        if self.game_mode == "Challenge":
            challenge_mods = {
                "One Life District": "Blackout",
                "Score Rush": "Harvest Grid",
                "Ghost Hunt": "Overdrive",
                "Neon Sprint": "Harvest Grid",
                "Phantom Debt": "Power Surge",
                "District Ace": "Blackout",
                "Redline Protocol": "Redline Sector",
                "Clock Reaper": "Null Pulse",
            }
            return challenge_mods.get(self.challenge_name, "Blackout")

        if self.game_mode == "Endless":
            cycle = ["Neon Calm", "Harvest Grid", "Overdrive", "Power Surge"]
            if "Redline Sector" in self.elite_district_names():
                cycle.append("Redline Sector")
            if "Null Pulse" in self.elite_district_names():
                cycle.append("Null Pulse")
            return cycle[(max(1, self.current_level) - 1) % len(cycle)]

        if self.game_mode == "Time Attack":
            cycle = ["Power Surge", "Harvest Grid", "Overdrive"]
            if "Null Pulse" in self.elite_district_names():
                cycle[1] = "Null Pulse"
            if "Redline Sector" in self.elite_district_names():
                cycle[2] = "Redline Sector"
            return cycle[min(max(1, self.current_level), len(cycle)) - 1]

        arcade_cycle = ("Neon Calm", "Overdrive", "Power Surge")
        return arcade_cycle[min(max(1, self.current_level), len(arcade_cycle)) - 1]

    def district_modifier(self) -> DistrictModifier:
        return DISTRICT_MODIFIERS[self.district_modifier_name()]

    def apply_difficulty(self, difficulty: str) -> None:
        preset = DIFFICULTY_PRESETS[difficulty]
        self.difficulty = difficulty

        self.cfg.logic_tick_rate = preset.logic_tick_rate
        self.cfg.rage_duration_ticks = preset.rage_duration_ticks
        self.cfg.cherry_respawn_ticks = preset.cherry_respawn_ticks
        self.cfg.ghost_chase_ticks = preset.ghost_chase_ticks
        self.cfg.ghost_scatter_ticks = preset.ghost_scatter_ticks
        self.cfg.ghost_release_tick_interval = preset.ghost_release_tick_interval
        self.cfg.initial_lives = preset.initial_lives
        self.cfg.seed_score = preset.seed_score
        self.cfg.large_seed_score = preset.large_seed_score
        self.cfg.cherry_score = preset.cherry_score
        self.cfg.ghost_score = preset.ghost_score

    def difficulty_summary_lines(self, difficulty: Optional[str] = None) -> tuple[str, str, str]:
        key = difficulty or self.difficulty
        return DIFFICULTY_PRESETS[key].summary_lines

    def reset_ghost_mode_cycle(self) -> None:
        self.ghost_mode = "chase"
        self.ghost_mode_timer = 0
        self.pressure_stage = 0

    def reset_ghost_combo(self) -> None:
        self.ghost_combo = 0

    def reset_power_chain(self) -> None:
        self.power_chain_level = 0
        self.power_chain_window = 0

    def reset_route_chain(self) -> None:
        self.route_chain_count = 0
        self.route_chain_window = 0
        self.run.line_chain_count = 0
        self.run.line_chain_dx = 0
        self.run.line_chain_dy = 0

    def route_chain_grace_ticks(self) -> int:
        if self.game_mode == "Time Attack":
            return 46
        if self.game_mode == "Endless":
            return 52
        return 58

    def tick_route_chain_window(self) -> None:
        if self.route_chain_window > 0:
            self.route_chain_window -= 1
            if self.route_chain_window == 0:
                self.reset_route_chain()

    def register_route_chain_dot(self) -> tuple[int, int]:
        if self.route_chain_window > 0:
            self.route_chain_count += 1
        else:
            self.route_chain_count = 1

        self.route_chain_window = self.route_chain_grace_ticks()

        bonus = 0
        if self.route_chain_count >= 6 and self.route_chain_count % 4 == 0:
            bonus = 40 + max(0, self.route_chain_count - 4) * 12
            bonus = int(bonus * self.mode_score_multiplier())
        return self.route_chain_count, bonus

    def register_line_bonus_dot(self, dx: int, dy: int) -> tuple[int, int]:
        if dx == 0 and dy == 0:
            self.run.line_chain_count = 0
            self.run.line_chain_dx = 0
            self.run.line_chain_dy = 0
            return 0, 0

        if (self.run.line_chain_dx, self.run.line_chain_dy) == (dx, dy):
            self.run.line_chain_count += 1
        else:
            self.run.line_chain_dx = dx
            self.run.line_chain_dy = dy
            self.run.line_chain_count = 1

        bonus = 0
        if self.run.line_chain_count >= 8 and self.run.line_chain_count % 4 == 0:
            bonus = 28 + max(0, self.run.line_chain_count - 8) * 10
            bonus = int(bonus * self.mode_score_multiplier())
        return self.run.line_chain_count, bonus

    def risk_turn_bonus_value(self) -> int:
        base = 70
        if self.game_mode == "Challenge":
            base = 95
        elif self.game_mode == "Time Attack":
            base = 85
        elif self.game_mode == "Endless":
            base = 78
        if self.pressure_stage >= 2:
            base += 18
        return int(base * self.mode_score_multiplier())

    def power_chain_grace_ticks(self) -> int:
        if self.game_mode == "Challenge":
            return 72
        if self.game_mode == "Endless":
            return 84
        return 96

    def begin_power_chain_window(self) -> None:
        if self.power_chain_level > 0:
            self.power_chain_window = self.power_chain_grace_ticks()

    def tick_power_chain_window(self) -> None:
        pacman = self.pacman
        if pacman is not None and getattr(pacman, "rage", False):
            return
        if self.power_chain_window > 0:
            self.power_chain_window -= 1
            if self.power_chain_window == 0:
                self.reset_power_chain()
                self.reset_ghost_combo()

    def trigger_power_chain(self, already_raging: bool) -> tuple[int, int, int, bool]:
        chained = already_raging or self.power_chain_window > 0
        if chained:
            self.power_chain_level += 1
        else:
            self.power_chain_level = 1
        self.power_chain_window = 0

        chain_bonus = max(0, self.power_chain_level - 1) * 150
        rage_bonus = max(0, self.power_chain_level - 1) * 36
        keep_combo = self.power_chain_level > 1
        return self.power_chain_level, chain_bonus, rage_bonus, keep_combo

    def next_ghost_combo_score(self) -> int:
        combo_step = min(self.ghost_combo, 3)
        chain_bonus = max(0, self.power_chain_level - 1) * 40
        base_score = self.cfg.ghost_score + self.district_modifier().ghost_score_bonus + self.current_map_trait().ghost_score_bonus + chain_bonus
        return int(base_score * (2 ** combo_step) * self.mode_score_multiplier())

    def compute_pressure_stage(self, remaining_pickups: int, total_pickups: int) -> int:
        if total_pickups <= 0:
            return min(3, max(0, min(3, self.current_level - 1) + self.mode_pressure_bonus()))

        ratio = remaining_pickups / max(1, total_pickups)
        level_pressure = max(0, self.current_level - 1)

        if ratio <= 0.18:
            stage = 3
        elif ratio <= 0.40:
            stage = 2
        elif ratio <= 0.68:
            stage = 1
        else:
            stage = 0

        return min(3, max(stage, min(2, level_pressure) + self.mode_pressure_bonus()))

    def elite_pressure_active(self) -> bool:
        if self.game_mode == "Challenge":
            return self.pressure_stage >= 2
        if self.game_mode == "Endless":
            return self.current_level >= 4 or self.pressure_stage >= 3
        return self.current_level >= 3 and self.pressure_stage >= 2

    def update_pressure_stage(self, remaining_pickups: int, total_pickups: int) -> bool:
        new_stage = self.compute_pressure_stage(remaining_pickups, total_pickups)
        changed = new_stage != self.pressure_stage
        self.pressure_stage = new_stage
        return changed

    def effective_ghost_cycle(self, pressure_stage: Optional[int] = None) -> tuple[int, int]:
        level_offset = max(0, self.current_level - 1)
        pressure = self.pressure_stage if pressure_stage is None else pressure_stage
        modifier = self.district_modifier()
        map_trait = self.current_map_trait()
        chase_ticks = self.cfg.ghost_chase_ticks + level_offset * self.cfg.ghost_chase_tick_step + pressure * 8 + modifier.chase_bonus + map_trait.chase_bonus
        scatter_ticks = max(
            self.cfg.ghost_scatter_tick_min,
            self.cfg.ghost_scatter_ticks - level_offset * self.cfg.ghost_scatter_tick_step - pressure * 6 - modifier.scatter_penalty - map_trait.scatter_penalty,
        )
        if self.elite_pressure_active():
            chase_ticks += 18
            scatter_ticks = max(self.cfg.ghost_scatter_tick_min, scatter_ticks - 8)
        return chase_ticks, scatter_ticks

    def effective_rage_duration(self) -> int:
        level_offset = max(0, self.current_level - 1)
        modifier = self.district_modifier()
        map_trait = self.current_map_trait()
        return max(
            self.cfg.rage_duration_tick_min,
            self.cfg.rage_duration_ticks - level_offset * self.cfg.rage_duration_tick_step + modifier.rage_bonus + map_trait.rage_bonus + self.mode_rage_bonus(),
        )

    def effective_cherry_respawn(self) -> int:
        level_offset = max(0, self.current_level - 1)
        modifier = self.district_modifier()
        map_trait = self.current_map_trait()
        return max(
            self.cfg.cherry_respawn_tick_min,
            self.cfg.cherry_respawn_ticks - level_offset * self.cfg.cherry_respawn_tick_step - modifier.cherry_respawn_bonus - map_trait.cherry_respawn_bonus,
        )

    def effective_cherry_score(self) -> int:
        level_offset = max(0, self.current_level - 1)
        value = self.cfg.cherry_score + level_offset * self.cfg.cherry_score_step + self.district_modifier().cherry_score_bonus + self.current_map_trait().cherry_score_bonus
        return int(value * self.mode_score_multiplier())

    def effective_seed_score(self) -> int:
        value = self.cfg.seed_score + self.district_modifier().seed_score_bonus
        return int(value * self.mode_score_multiplier())

    def effective_large_seed_score(self) -> int:
        level_offset = max(0, self.current_level - 1)
        value = self.cfg.large_seed_score + level_offset * self.cfg.large_seed_score_step + self.district_modifier().large_seed_bonus
        return int(value * self.mode_score_multiplier())

    def effective_ghost_release_interval(self) -> int:
        level_offset = max(0, self.current_level - 1)
        modifier = self.district_modifier()
        map_trait = self.current_map_trait()
        interval = max(
            self.cfg.ghost_release_tick_min,
            self.cfg.ghost_release_tick_interval - level_offset * self.cfg.ghost_release_tick_step - modifier.release_bonus - map_trait.release_bonus,
        )
        if self.elite_pressure_active():
            interval = max(self.cfg.ghost_release_tick_min, interval - 2)
        return interval

    def effective_item_counts(self) -> tuple[int, int, int] | None:
        if self.game_map is None:
            return None
        return self.game_map.item_counts()

    def advance_ghost_mode_cycle(self, remaining_pickups: Optional[int] = None, total_pickups: Optional[int] = None) -> bool:
        pressure_changed = False
        if remaining_pickups is not None and total_pickups is not None:
            pressure_changed = self.update_pressure_stage(remaining_pickups, total_pickups)

        self.ghost_mode_timer += 1

        chase_ticks, scatter_ticks = self.effective_ghost_cycle()
        cycle_length = chase_ticks + scatter_ticks
        cycle_tick = self.ghost_mode_timer % cycle_length

        if cycle_tick < chase_ticks:
            self.ghost_mode = "chase"
        else:
            self.ghost_mode = "scatter"
        return pressure_changed

    def get_map_path(self, level: Optional[int] = None) -> str:
        """Get the map file path for a given level (1-indexed)."""
        level = level or self.current_level
        if self.game_mode == "Challenge":
            cycle = self.challenge_preset().map_cycle
        else:
            cycle = self.game_mode_preset().map_cycle
        map_number = cycle[(max(1, level) - 1) % len(cycle)]
        if map_number == 1:
            return "maps/pacman_map.txt"
        return f"maps/pacman_map{map_number}.txt"

    def current_map_number(self, level: Optional[int] = None) -> int:
        level = level or self.current_level
        if self.game_mode == "Challenge":
            cycle = self.challenge_preset().map_cycle
        else:
            cycle = self.game_mode_preset().map_cycle
        return cycle[(max(1, level) - 1) % len(cycle)]

    def current_map_trait(self) -> MapTrait:
        return MAP_TRAITS.get(self.current_map_number(), MAP_TRAITS[1])

    def arcade_campaign_chapter(self, level: Optional[int] = None) -> Optional[ArcadeChapter]:
        if self.game_mode != "Arcade":
            return None
        chapter_index = min(max(1, level or self.current_level), len(ARCADE_CHAPTERS)) - 1
        return ARCADE_CHAPTERS[chapter_index]

    def arcade_campaign_summary_lines(self) -> tuple[str, str, str]:
        chapter = self.arcade_campaign_chapter()
        if chapter is None:
            return self.mode_summary_lines()
        return (
            chapter.title,
            chapter.subtitle,
            chapter.briefing,
        )

    def map_link_bonus_value(self) -> int:
        return 120 if self.current_map_number() == 1 else 0

    def map_link_bonus_step(self) -> int:
        return 60 if self.current_map_number() == 1 else 0

    def map_cherry_bonus_value(self) -> int:
        return 200 if self.current_map_number() == 4 else 0

    def map_ghost_rage_extension(self) -> int:
        return 22 if self.current_map_number() == 3 else 0

    def map_release_surge_amount(self) -> int:
        if self.current_map_number() == 5:
            return 5
        if self.current_map_number() == 2:
            return 3
        return 0

    def map_blinky_bias(self) -> float:
        number = self.current_map_number()
        if number == 5:
            return -0.55
        if number == 2:
            return -0.35
        return 0.0

    def map_pinky_bias(self) -> float:
        number = self.current_map_number()
        if number == 4:
            return -0.5
        if number == 1:
            return -0.2
        return 0.0

    def map_inky_bias(self) -> float:
        number = self.current_map_number()
        if number == 1:
            return -0.45
        if number == 3:
            return -0.2
        return 0.0

    def map_clyde_bias(self) -> float:
        number = self.current_map_number()
        if number == 3:
            return -0.5
        if number == 4:
            return 0.2
        return 0.0

    def run_won_on_level_clear(self) -> bool:
        if self.game_mode == "Challenge":
            return False
        total_levels = self.total_levels_for_mode()
        if total_levels is None:
            return False
        return self.current_level >= total_levels

    def challenge_result_on_clear(self) -> str:
        preset = self.challenge_preset()
        if preset.target_score > 0 and self.score < preset.target_score:
            return "challenge_failed"
        if preset.target_ghosts > 0 and self.run_stats.ghosts_eaten < preset.target_ghosts:
            return "challenge_failed"
        return "game_won"

    def next_level(self) -> None:
        """Advance to the next level."""
        if self.game_mode == "Time Attack":
            self.time_attack_seconds += self.time_attack_clear_bonus_seconds()
        self.current_level += 1
        if self.game_mode_preset().reset_lives_each_level:
            self.lives = self.starting_lives()
        self.mark_level_baseline()

    def record_dot_eaten(self) -> None:
        self.run_stats.dots_eaten += 1

    def route_chain_active(self) -> bool:
        return self.route_chain_count >= 4 and self.route_chain_window > 0

    def record_power_seed_eaten(self) -> None:
        self.run_stats.power_seeds_eaten += 1

    def record_cherry_eaten(self) -> None:
        self.run_stats.cherries_eaten += 1

    def record_ghost_eaten(self) -> None:
        self.run_stats.ghosts_eaten += 1

    def record_level_cleared(self) -> None:
        self.run_stats.levels_cleared += 1
        self.profile["total_levels_cleared"] += 1
        self.profile["highest_level"] = max(self.profile["highest_level"], self.current_level)
        self.save_profile()

    def finalize_run_result(self, result: str) -> None:
        if self.run_stats.finalized:
            return

        self.run_stats.finalized = True
        before_snapshot = self.pre_run_unlock_snapshot or self.unlock_snapshot()
        if result == "game_won":
            self.profile["total_wins"] += 1
        elif result in {"lose", "challenge_failed"}:
            self.profile["total_losses"] += 1

        self.profile["best_score"] = max(self.profile["best_score"], self.score)
        self.profile["highest_level"] = max(self.profile["highest_level"], self.current_level)
        self.profile["total_dots_eaten"] += self.run_stats.dots_eaten
        self.profile["total_power_seeds"] += self.run_stats.power_seeds_eaten
        self.profile["total_cherries"] += self.run_stats.cherries_eaten
        self.profile["total_ghosts_eaten"] += self.run_stats.ghosts_eaten
        self.profile.setdefault("mode_mastery", {"Arcade": 0, "Endless": 0, "Challenge": 0})
        self.profile.setdefault("challenge_credits", 0)
        self.profile.setdefault("challenge_clears", 0)
        self.profile.setdefault("challenge_streak", 0)
        self.profile.setdefault("best_challenge_streak", 0)
        mastery_gain = self.mode_mastery_gain(result)
        self.profile["mode_mastery"][self.game_mode] = int(self.profile["mode_mastery"].get(self.game_mode, 0)) + mastery_gain
        if result == "game_won" and self.game_mode == "Challenge":
            self.profile.setdefault("challenge_rewards", {})
            self.profile["challenge_rewards"][self.challenge_name] = 1
            self.profile["challenge_clears"] = int(self.profile.get("challenge_clears", 0)) + 1
            self.profile["challenge_streak"] = int(self.profile.get("challenge_streak", 0)) + 1
            self.profile["best_challenge_streak"] = max(
                int(self.profile.get("best_challenge_streak", 0)),
                int(self.profile.get("challenge_streak", 0)),
            )
        elif self.game_mode == "Challenge":
            self.profile["challenge_streak"] = 0
        self.profile["challenge_credits"] = int(self.profile.get("challenge_credits", 0)) + self.challenge_credit_reward(result)
        challenge_title = self.challenge_preset().title if self.game_mode == "Challenge" else ""
        self.profile.setdefault("run_history", [])
        self.profile["run_history"].insert(
            0,
            {
                "mode": self.game_mode,
                "challenge": challenge_title,
                "difficulty": self.difficulty,
                "result": result,
                "score": self.score,
                "level": self.current_level,
            },
        )
        self.profile["run_history"] = self.profile["run_history"][:12]
        self.last_unlock_lines = self.new_unlock_lines(before_snapshot)
        self.save_profile()

    def save_profile(self) -> None:
        self.profile_service.save()

    def unlock_snapshot(self) -> dict:
        return {
            "rank": self.rank_title(),
            "challenge_rank": self.challenge_track_rank(),
            "mode_ranks": {
                mode: self.mode_mastery_rank(mode)
                for mode in GAME_MODE_PRESETS.keys()
            },
            "themes": {
                name for name, _preset, unlocked in self.theme_entries()
                if unlocked
            },
            "hud_packs": {
                name for name, _preset, unlocked in self.hud_pack_entries()
                if unlocked
            },
            "title_variants": {
                name for name, _preset, unlocked in self.title_variant_entries()
                if unlocked
            },
            "directive_packs": self.directive_pack_names(),
            "elite_districts": self.elite_district_names(),
            "challenges": {
                name for name, _preset, unlocked in self.challenge_entries()
                if unlocked
            },
            "achievements": {
                title for title, _detail, unlocked in self.achievement_entries()
                if unlocked
            },
            "challenge_rewards": {
                name for name in CHALLENGE_PRESETS.keys()
                if self.challenge_reward_unlocked(name)
            },
        }

    def _collect_new_unlock_lines(self, before: Optional[dict] = None) -> list[str]:
        before = before or {}
        after = self.unlock_snapshot()
        lines: list[str] = []

        if before.get("rank") and before.get("rank") != after["rank"]:
            lines.append(f"Career Rank -> {after['rank']}")

        if before.get("challenge_rank") and before.get("challenge_rank") != after["challenge_rank"]:
            lines.append(f"Challenge Rank -> {after['challenge_rank']}")

        before_mode_ranks = before.get("mode_ranks", {})
        for mode, rank in after["mode_ranks"].items():
            if before_mode_ranks.get(mode) and before_mode_ranks.get(mode) != rank:
                lines.append(f"{mode} Mastery -> {rank}")

        new_themes = sorted(after["themes"] - before.get("themes", set()))
        for name in new_themes:
            lines.append(f"Theme Unlocked: {name.upper()}")

        new_hud_packs = sorted(after["hud_packs"] - before.get("hud_packs", set()))
        for name in new_hud_packs:
            lines.append(f"HUD Pack Unlocked: {name.upper()}")

        new_title_variants = sorted(after["title_variants"] - before.get("title_variants", set()))
        for name in new_title_variants:
            lines.append(f"Title Variant: {name.upper()}")

        new_directive_packs = sorted(after["directive_packs"] - before.get("directive_packs", set()))
        for name in new_directive_packs:
            if name != "Core Directives":
                lines.append(f"Directive Pack: {name.upper()}")

        new_elite_districts = sorted(after["elite_districts"] - before.get("elite_districts", set()))
        for name in new_elite_districts:
            lines.append(f"Elite District: {name.upper()}")

        new_challenges = sorted(after["challenges"] - before.get("challenges", set()))
        for name in new_challenges:
            lines.append(f"Trial Unlocked: {CHALLENGE_PRESETS[name].title}")

        new_achievements = sorted(after["achievements"] - before.get("achievements", set()))
        for title in new_achievements:
            lines.append(f"Achievement: {title}")

        new_rewards = sorted(after["challenge_rewards"] - before.get("challenge_rewards", set()))
        for name in new_rewards:
            lines.append(f"Trophy Earned: {CHALLENGE_PRESETS[name].reward_title}")

        return lines

    def new_unlock_lines(self, before: Optional[dict] = None) -> tuple[str, str, str]:
        lines = self._collect_new_unlock_lines(before)
        self.last_unlocks_are_new = bool(lines)

        if not lines:
            next_goals = [line for line in self.career_goal_lines() if line]
            while len(next_goals) < 3:
                next_goals.append("Keep pushing the district")
            return (next_goals[0], next_goals[1], next_goals[2])

        while len(lines) < 3:
            lines.append("More unlocks waiting in Career")
        return (lines[0], lines[1], lines[2])

    def profile_save_summary_lines(self) -> tuple[str, str, str]:
        return (
            "AUTO-SAVE ACTIVE",
            f"FILE {PROFILE_FILE.name.upper()}",
            f"RUNS {int(self.profile.get('total_runs', 0))}  HISTORY {len(self.run_history_entries())}",
        )

    def reward_showcase_lines(self) -> tuple[str, str, str]:
        if self.last_unlocks_are_new:
            return self.last_unlock_lines
        reward_lines = list(self.reward_progress_lines())
        reward_lines[0] = "NO NEW UNLOCK THIS RUN"
        return (reward_lines[0], reward_lines[1], reward_lines[2])

    def fx_intensity(self) -> str:
        return self.settings.get_string("fx_intensity", "High")

    def set_fx_intensity(self, value: str) -> None:
        if value not in {"Low", "Medium", "High"}:
            return
        self.settings.set_string("fx_intensity", value)

    def screen_flash_enabled(self) -> bool:
        return self.settings.get_bool("screen_flash", True)

    def set_screen_flash_enabled(self, enabled: bool) -> None:
        self.settings.set_bool("screen_flash", enabled)

    def screen_shake_enabled(self) -> bool:
        return self.settings.get_bool("screen_shake", True)

    def set_screen_shake_enabled(self, enabled: bool) -> None:
        self.settings.set_bool("screen_shake", enabled)

    def music_enabled(self) -> bool:
        return self.settings.get_bool("music_enabled", True)

    def set_music_enabled(self, enabled: bool) -> None:
        self.settings.set_bool("music_enabled", enabled)

    def sfx_enabled(self) -> bool:
        return self.settings.get_bool("sfx_enabled", True)

    def set_sfx_enabled(self, enabled: bool) -> None:
        self.settings.set_bool("sfx_enabled", enabled)

    def tutorial_enabled(self) -> bool:
        return self.settings.get_bool("tutorial_enabled", True)

    def set_tutorial_enabled(self, enabled: bool) -> None:
        self.settings.set_bool("tutorial_enabled", enabled)

    def tutorial_seen(self) -> bool:
        return bool(self.profile.get("tutorial_seen", 0))

    def mark_tutorial_seen(self) -> None:
        self.profile["tutorial_seen"] = 1
        self.save_profile()

    def reset_tutorial_seen(self) -> None:
        self.profile["tutorial_seen"] = 0
        self.save_profile()

    def capture_mode_enabled(self) -> bool:
        return self.settings.get_bool("capture_mode", False)

    def set_capture_mode_enabled(self, enabled: bool, *, save: bool = True) -> None:
        self.settings.set_bool("capture_mode", enabled, save=False)
        from ui import ui as ui_theme
        ui_theme.set_presentation_mode(enabled)
        if save:
            self.save_profile()

    def onboarding_summary_lines(self) -> tuple[str, str, str]:
        if not self.tutorial_enabled():
            return (
                "Training disabled",
                "Turn it on to show first-run guidance",
                "Replay is always available from Options",
            )
        if self.tutorial_seen():
            return (
                "Training completed",
                "Replay tutorial if you want a guided refresher",
                "Gameplay hints stay hidden during normal runs",
            )
        return (
            "Training armed",
            "Your next run starts with guided movement and power-seed hints",
            "Finish the four onboarding steps to clear it",
        )

    def fx_multiplier(self) -> float:
        intensity = self.fx_intensity()
        if intensity == "Low":
            return 0.55
        if intensity == "Medium":
            return 0.8
        return 1.0

    def trigger_screen_shake(self, intensity: float, duration: float) -> None:
        if not self.screen_shake_enabled():
            return
        scale = self.fx_multiplier()
        self.screen_shake.shake(intensity * scale, duration)

    def trigger_screen_flash(self, color, intensity: float, duration: float) -> None:
        if not self.screen_flash_enabled():
            return
        scale = self.fx_multiplier()
        self.screen_flash.flash(color, intensity * scale, duration)

    def play_sfx(self, name: str) -> None:
        if self.audio_manager is None:
            return
        try:
            self.audio_manager.play_sfx(name, self)
        except Exception:
            pass

    def unlocked_milestones(self) -> list[tuple[str, str]]:
        return [
            (title, detail)
            for title, detail, unlocked in self.achievement_entries()
            if unlocked
        ]

    def next_achievement_goal(self) -> Optional[str]:
        for title, detail, unlocked in self.achievement_entries():
            if not unlocked:
                return f"{title}: {detail}"
        return None

    def mode_mastery_gain(self, result: str) -> int:
        gain = 1
        if result == "level_complete":
            gain += 1
        elif result == "game_won":
            gain += 3
        elif result == "challenge_failed":
            gain += 1

        gain += min(3, self.current_level - 1)
        gain += min(2, self.run_stats.ghosts_eaten // 2)
        return gain

    def mode_mastery_value(self, mode: str) -> int:
        mastery = self.profile.get("mode_mastery", {})
        return int(mastery.get(mode, 0))

    def mode_mastery_rank(self, mode: str) -> str:
        value = self.mode_mastery_value(mode)
        if value >= 30:
            return "MASTER"
        if value >= 18:
            return "ELITE"
        if value >= 9:
            return "PRO"
        if value >= 3:
            return "INITIATE"
        return "UNRANKED"

    def next_mode_mastery_goal(self) -> Optional[str]:
        mode = min(
            GAME_MODE_PRESETS.keys(),
            key=lambda name: (self.mode_mastery_value(name), name),
        )
        value = self.mode_mastery_value(mode)
        for threshold, title in MODE_MASTERY_THRESHOLDS:
            if value < threshold:
                return f"{mode}: {title} at {threshold}  ({threshold - value} to go)"
        return None

    def mode_mastery_summary_lines(self) -> tuple[str, str, str]:
        return (
            f"Arcade {self.mode_mastery_rank('Arcade')} {self.mode_mastery_value('Arcade')}",
            f"Endless {self.mode_mastery_rank('Endless')} {self.mode_mastery_value('Endless')}",
            f"Challenge {self.mode_mastery_rank('Challenge')} {self.mode_mastery_value('Challenge')}  Time {self.mode_mastery_rank('Time Attack')} {self.mode_mastery_value('Time Attack')}",
        )

    def achievement_entries(self) -> list[tuple[str, str, bool]]:
        profile = self.profile
        return [
            (title, detail, bool(check(profile)))
            for title, detail, check in ACHIEVEMENT_DEFS
        ]

    def achievement_summary_lines(self) -> tuple[str, str, str]:
        entries = self.achievement_entries()
        unlocked = sum(1 for _title, _detail, is_open in entries if is_open)
        total = len(entries)
        return (
            f"Unlocked {unlocked}/{total}",
            f"Rank {self.rank_title()}",
            f"Best Score {self.profile['best_score']}",
        )

    def rank_title(self) -> str:
        score = (
            self.profile["best_score"]
            + self.profile["total_levels_cleared"] * 400
            + self.profile["total_ghosts_eaten"] * 30
            + self.profile["total_wins"] * 1200
            + self.mode_mastery_value("Arcade") * 70
            + self.mode_mastery_value("Endless") * 90
            + self.mode_mastery_value("Challenge") * 110
        )
        if score >= 12000:
            return "NEON LEGEND"
        if score >= 7000:
            return "DISTRICT ACE"
        if score >= 3500:
            return "ARCADE HUNTER"
        if score >= 1200:
            return "NIGHT RUNNER"
        return "ROOKIE PILOT"

    def career_rank_score(self) -> int:
        return (
            self.profile["best_score"]
            + self.profile["total_levels_cleared"] * 400
            + self.profile["total_ghosts_eaten"] * 30
            + self.profile["total_wins"] * 1200
            + self.mode_mastery_value("Arcade") * 70
            + self.mode_mastery_value("Endless") * 90
            + self.mode_mastery_value("Challenge") * 110
        )

    def next_rank_goal(self) -> Optional[str]:
        score = self.career_rank_score()
        for threshold, title in RANK_THRESHOLDS:
            if score < threshold:
                return f"{title} at {threshold} rank pts  ({threshold - score} to go)"
        return None

    def profile_summary_lines(self) -> tuple[str, str, str]:
        milestones = len(self.unlocked_milestones())
        return (
            f"Runs {self.profile['total_runs']}  Wins {self.profile['total_wins']}",
            f"Best {self.profile['best_score']}  Level {self.profile['highest_level']}",
            f"Milestones {milestones}  Ghosts {self.profile['total_ghosts_eaten']}",
        )

    def mode_run_summary_lines(self) -> tuple[str, str, str]:
        mode_runs = self.profile.get("mode_runs", {})
        return (
            f"Arcade {int(mode_runs.get('Arcade', 0))}  Endless {int(mode_runs.get('Endless', 0))}",
            f"Challenge {int(mode_runs.get('Challenge', 0))}  Time {int(mode_runs.get('Time Attack', 0))}",
            f"Total Runs {int(self.profile.get('total_runs', 0))}",
        )

    def difficulty_run_summary_lines(self) -> tuple[str, str, str]:
        difficulty_runs = self.profile.get("difficulty_runs", {})
        return (
            f"Easy Runs {int(difficulty_runs.get('Easy', 0))}",
            f"Normal Runs {int(difficulty_runs.get('Normal', 0))}",
            f"Hard Runs {int(difficulty_runs.get('Hard', 0))}",
        )

    def lifetime_stat_lines(self) -> tuple[str, str, str]:
        profile = self.profile
        return (
            f"Dots {profile['total_dots_eaten']}  Power {profile['total_power_seeds']}",
            f"Cherries {profile['total_cherries']}  Ghosts {profile['total_ghosts_eaten']}",
            f"Levels {profile['total_levels_cleared']}  Losses {profile['total_losses']}",
        )

    def next_challenge_unlock_goal(self) -> Optional[str]:
        for name, preset, unlocked in self.challenge_entries():
            if not unlocked:
                return f"{preset.title}: {preset.unlock_text.replace('Unlock: ', '')}"
        return None

    def career_goal_lines(self) -> tuple[str, str, str]:
        goals = [
            self.next_rank_goal(),
            self.next_challenge_unlock_goal(),
            self.next_theme_goal(),
            self.next_hud_pack_goal(),
            self.next_title_variant_goal(),
            self.next_directive_pack_goal(),
            self.next_elite_district_goal(),
            self.next_mode_mastery_goal(),
            self.next_challenge_rank_goal(),
            self.next_achievement_goal(),
        ]
        lines = [goal for goal in goals if goal]
        if not lines:
            return (
                "Career file fully lit",
                "All visible goals are complete",
                "Push score and mastery for prestige",
            )
        while len(lines) < 3:
            lines.append("Keep pushing runs to unlock more")
        return (lines[0], lines[1], lines[2])

    def run_history_entries(self) -> list[dict]:
        history = self.profile.get("run_history", [])
        if not isinstance(history, list):
            return []
        return history[:12]

    def run_history_summary_lines(self) -> tuple[str, str, str]:
        entries = self.run_history_entries()
        if not entries:
            return (
                "No finished runs logged yet",
                f"Mode {self.mode_label()}  Difficulty {self.difficulty}",
                "Complete a run to populate the journal",
            )
        latest = entries[0]
        tag = latest.get("challenge") or latest.get("mode", "Arcade")
        return (
            f"Logged Runs {len(entries)}",
            f"Latest {tag} / {latest.get('difficulty', 'Normal')}",
            f"Latest Score {int(latest.get('score', 0))}",
        )

    def journal_summary_lines(self) -> tuple[str, str, str]:
        districts_open = sum(1 for _title, _subtitle, _detail, _accent, unlocked in self.district_journal_entries() if unlocked)
        trials_open = sum(1 for _title, _subtitle, _reward, _accent, unlocked in self.challenge_journal_entries() if unlocked)
        ghosts_known = len(self.ghost_journal_entries())
        return (
            f"District Files {districts_open}/{len(self.district_journal_entries())}",
            f"Trial Files {trials_open}/{len(self.challenge_journal_entries())}",
            f"Ghost Files {ghosts_known}/4",
        )

    def district_journal_entries(self) -> list[tuple[str, str, str, object, bool]]:
        entries: list[tuple[str, str, str, object, bool]] = []
        district_notes = {
            1: "Fast cherries, angled ambush lanes",
            2: "Heavy release pressure, shorter safe windows",
            3: "Short rage, richer ghost reward routing",
            4: "Bonus-heavy market tempo and relay routes",
            5: "Survival board with escalating pressure spikes",
        }
        for map_number in sorted(MAP_TRAITS.keys()):
            trait = MAP_TRAITS[map_number]
            entries.append((trait.title, trait.subtitle, district_notes.get(map_number, "District routing file"), trait.accent, True))

        elite_notes = {
            "Redline Sector": "Elite overrun pattern with score-heavy pressure",
            "Null Pulse": "Cold precision district with shorter power windows",
        }
        for name in ("Redline Sector", "Null Pulse"):
            modifier = DISTRICT_MODIFIERS[name]
            entries.append((modifier.title, modifier.subtitle, elite_notes[name], modifier.accent, name in self.elite_district_names()))
        return entries

    def challenge_journal_entries(self) -> list[tuple[str, str, str, object, bool]]:
        entries: list[tuple[str, str, str, object, bool]] = []
        for name, preset in CHALLENGE_PRESETS.items():
            entries.append((preset.title, f"{preset.board_tag}  {preset.threat_label}", preset.reward_title, preset.accent, self.challenge_unlocked(name)))
        return entries

    def ghost_journal_entries(self) -> list[tuple[str, str, str, object]]:
        return [
            ("BLINKY", "Relentless direct chase", "Gets nastier in Pressure Lanes and Credit Spiral", colors.RED),
            ("PINKY", "Front-cut ambush routes", "Excels in Transit Grid and Market Loop", colors.MAGENTA),
            ("INKY", "Side-angle intercept logic", "Harder to read on Transit Grid", colors.SKYBLUE),
            ("CLYDE", "Skittish until he gets close", "Turns meaner in Black Channel", colors.ORANGE),
        ]
