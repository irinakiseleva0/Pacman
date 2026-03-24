from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from raylib import colors

from ui.layout import DEFAULT_LAYOUT, LAYOUT_PROFILES
from utils.profile_storage import load_profile, save_profile
from utils.score_storage import load_high_score
from utils.visual_effects import ParticleSystem, ScreenShake, FloatingTextSystem, ScreenFlash


@dataclass(frozen=True)
class DifficultyPreset:
    logic_tick_rate: int
    rage_duration_ticks: int
    cherry_respawn_ticks: int
    ghost_chase_ticks: int
    ghost_scatter_ticks: int
    ghost_release_tick_interval: int
    initial_lives: int
    seed_score: int
    large_seed_score: int
    cherry_score: int
    ghost_score: int
    summary_lines: tuple[str, str, str]


@dataclass
class RunStats:
    dots_eaten: int = 0
    power_seeds_eaten: int = 0
    cherries_eaten: int = 0
    ghosts_eaten: int = 0
    levels_cleared: int = 0
    level_start_score: int = 0
    level_start_dots: int = 0
    level_start_power_seeds: int = 0
    level_start_cherries: int = 0
    level_start_ghosts: int = 0
    finalized: bool = False


@dataclass(frozen=True)
class GameModePreset:
    title: str
    subtitle: str
    summary_lines: tuple[str, str, str]
    accent: tuple[int, int, int, int]
    max_levels: Optional[int] = None
    map_cycle: tuple[int, ...] = (1, 2, 3)
    reset_lives_each_level: bool = True


@dataclass(frozen=True)
class ChallengePreset:
    title: str
    subtitle: str
    summary_lines: tuple[str, str, str]
    accent: tuple[int, int, int, int]
    map_cycle: tuple[int, ...]
    starting_lives: int
    target_score: int = 0
    target_ghosts: int = 0
    unlock_text: str = "Available from the start"
    reward_title: str = "DISTRICT TOKEN"


@dataclass(frozen=True)
class ThemePreset:
    title: str
    subtitle: str
    unlock_text: str


@dataclass(frozen=True)
class DistrictModifier:
    title: str
    subtitle: str
    accent: tuple[int, int, int, int]
    chase_bonus: int = 0
    scatter_penalty: int = 0
    release_bonus: int = 0
    rage_bonus: int = 0
    cherry_respawn_bonus: int = 0
    cherry_score_bonus: int = 0
    large_seed_bonus: int = 0
    ghost_score_bonus: int = 0
    seed_score_bonus: int = 0


@dataclass(frozen=True)
class RunDirective:
    title: str
    subtitle: str
    kind: str
    target_value: int
    bonus_score: int
    accent: tuple[int, int, int, int]


@dataclass(frozen=True)
class MapTrait:
    title: str
    subtitle: str
    accent: tuple[int, int, int, int]
    chase_bonus: int = 0
    scatter_penalty: int = 0
    release_bonus: int = 0
    rage_bonus: int = 0
    cherry_respawn_bonus: int = 0
    cherry_score_bonus: int = 0
    ghost_score_bonus: int = 0


DIFFICULTY_PRESETS: dict[str, DifficultyPreset] = {
    "Easy": DifficultyPreset(
        logic_tick_rate=2,
        rage_duration_ticks=450,
        cherry_respawn_ticks=200,
        ghost_chase_ticks=90,
        ghost_scatter_ticks=70,
        ghost_release_tick_interval=24,
        initial_lives=5,
        seed_score=15,
        large_seed_score=75,
        cherry_score=750,
        ghost_score=300,
        summary_lines=(
            "Lives: 5  Rage: long",
            "Ghosts: lighter pressure, slower release",
            "Score: generous rewards",
        ),
    ),
    "Normal": DifficultyPreset(
        logic_tick_rate=3,
        rage_duration_ticks=300,
        cherry_respawn_ticks=150,
        ghost_chase_ticks=120,
        ghost_scatter_ticks=40,
        ghost_release_tick_interval=18,
        initial_lives=3,
        seed_score=10,
        large_seed_score=50,
        cherry_score=500,
        ghost_score=200,
        summary_lines=(
            "Lives: 3  Rage: standard",
            "Ghosts: balanced pressure",
            "Score: standard rewards",
        ),
    ),
    "Hard": DifficultyPreset(
        logic_tick_rate=4,
        rage_duration_ticks=200,
        cherry_respawn_ticks=100,
        ghost_chase_ticks=150,
        ghost_scatter_ticks=25,
        ghost_release_tick_interval=12,
        initial_lives=2,
        seed_score=5,
        large_seed_score=25,
        cherry_score=250,
        ghost_score=100,
        summary_lines=(
            "Lives: 2  Rage: short",
            "Ghosts: aggressive pressure, fast release",
            "Score: reduced rewards",
        ),
    ),
}


GAME_MODE_PRESETS: dict[str, GameModePreset] = {
    "Arcade": GameModePreset(
        title="ARCADE",
        subtitle="Classic three-district run",
        summary_lines=(
            "Three curated districts in sequence",
            "Lives refresh between districts",
            "Best mode for a full campaign-style run",
        ),
        accent=colors.SKYBLUE,
        max_levels=3,
        map_cycle=(1, 4, 5),
        reset_lives_each_level=True,
    ),
    "Endless": GameModePreset(
        title="ENDLESS",
        subtitle="Infinite district loop",
        summary_lines=(
            "District layouts loop forever",
            "Keep your remaining lives between clears",
            "Built for score chasing and long sessions",
        ),
        accent=colors.GOLD,
        max_levels=None,
        map_cycle=(1, 2, 3, 4, 5),
        reset_lives_each_level=False,
    ),
    "Challenge": GameModePreset(
        title="CHALLENGE",
        subtitle="One brutal district, one life",
        summary_lines=(
            "Drops you into the hardest district layout",
            "You get one life for the whole run",
            "Clear the board to log a prestige win",
        ),
        accent=colors.MAGENTA,
        max_levels=1,
        map_cycle=(3, 5),
        reset_lives_each_level=False,
    ),
}


CHALLENGE_PRESETS: dict[str, ChallengePreset] = {
    "One Life District": ChallengePreset(
        title="ONE LIFE",
        subtitle="Clear the district with one life",
        summary_lines=(
            "Drops you into the hardest district",
            "One life only, no refresh, no excuses",
            "Clear the board to complete the trial",
        ),
        accent=colors.MAGENTA,
        map_cycle=(3,),
        starting_lives=1,
        unlock_text="Available from the start",
        reward_title="ONE LIFE SIGIL",
    ),
    "Score Rush": ChallengePreset(
        title="SCORE RUSH",
        subtitle="Clear and finish above 3200",
        summary_lines=(
            "Clear District 2 with a score target",
            "Need 3200 points or more at the finish",
            "High pressure route-planning challenge",
        ),
        accent=colors.GOLD,
        map_cycle=(2,),
        starting_lives=2,
        target_score=3200,
        unlock_text="Unlock: finish 3 total runs",
        reward_title="RUSH CIRCUIT",
    ),
    "Ghost Hunt": ChallengePreset(
        title="GHOST HUNT",
        subtitle="Clear and eat 4 ghosts",
        summary_lines=(
            "Play the hard district with 2 lives",
            "You must eat at least 4 ghosts in-run",
            "Balance survival with aggressive routing",
        ),
        accent=colors.SKYBLUE,
        map_cycle=(3,),
        starting_lives=2,
        target_ghosts=4,
        unlock_text="Unlock: eat 10 ghosts total",
        reward_title="HUNTER EMBLEM",
    ),
    "Neon Sprint": ChallengePreset(
        title="NEON SPRINT",
        subtitle="Clear District 1 above 1800",
        summary_lines=(
            "Fast clear on the opening district",
            "You need 1800 score by board clear",
            "Built around clean routing and tempo",
        ),
        accent=colors.GREEN,
        map_cycle=(4,),
        starting_lives=2,
        target_score=1800,
        unlock_text="Unlock: reach level 2",
        reward_title="SPRINT STRIP",
    ),
    "Phantom Debt": ChallengePreset(
        title="PHANTOM DEBT",
        subtitle="One life, eat 6 ghosts",
        summary_lines=(
            "Single-life pressure on District 2",
            "Need to eat 6 ghosts before the clear",
            "Demands brave power-seed routing",
        ),
        accent=colors.ORANGE,
        map_cycle=(2,),
        starting_lives=1,
        target_ghosts=6,
        unlock_text="Unlock: win 1 run",
        reward_title="PHANTOM MARK",
    ),
    "District Ace": ChallengePreset(
        title="DISTRICT ACE",
        subtitle="Clear District 3 above 4200",
        summary_lines=(
            "Late-district prestige score challenge",
            "Reach 4200 by the end of the clear",
            "The harshest score target in the board",
        ),
        accent=colors.VIOLET,
        map_cycle=(3,),
        starting_lives=2,
        target_score=4200,
        unlock_text="Unlock: best score 3500",
        reward_title="ACE CREST",
    ),
    "Midnight Relay": ChallengePreset(
        title="MIDNIGHT RELAY",
        subtitle="Clear District 1 and eat 3 ghosts",
        summary_lines=(
            "Compact opening-district relay trial",
            "Need 3 ghost eats before the clear",
            "Short route, fast commitment",
        ),
        accent=colors.BLUE,
        map_cycle=(4,),
        starting_lives=2,
        target_ghosts=3,
        unlock_text="Unlock: clear 1 level",
        reward_title="RELAY BAND",
    ),
    "Credit Burner": ChallengePreset(
        title="CREDIT BURNER",
        subtitle="One life, clear above 2600",
        summary_lines=(
            "One-life score run on District 2",
            "Need 2600 points by board clear",
            "A clean route with no panic deaths",
        ),
        accent=colors.YELLOW,
        map_cycle=(5,),
        starting_lives=1,
        target_score=2600,
        unlock_text="Unlock: total score 2000",
        reward_title="BURNER CHIP",
    ),
    "Last Call": ChallengePreset(
        title="LAST CALL",
        subtitle="Clear District 3 and eat 8 ghosts",
        summary_lines=(
            "Late-board ghost pressure challenge",
            "Eat 8 ghosts before the district ends",
            "Built for long power-chain routing",
        ),
        accent=colors.PINK,
        map_cycle=(3,),
        starting_lives=2,
        target_ghosts=8,
        unlock_text="Unlock: eat 20 ghosts total",
        reward_title="LAST CALL PASS",
    ),
}


THEME_PRESETS: dict[str, ThemePreset] = {
    "Neon District": ThemePreset("NEON DISTRICT", "Classic cyan-magenta night", "Available from the start"),
    "Amber Rain": ThemePreset("AMBER RAIN", "Warm gold rain-soaked signage", "Unlock: win 1 run"),
    "Ice Circuit": ThemePreset("ICE CIRCUIT", "Cold cyan and steel palette", "Unlock: 2 trial trophies"),
    "Velvet Alley": ThemePreset("VELVET ALLEY", "Magenta-heavy moody street look", "Unlock: best score 5000"),
    "Grid Echo": ThemePreset("GRID ECHO", "Arcade mastery cyan-grid pack", "Unlock: Arcade mastery PRO"),
    "After Hours": ThemePreset("AFTER HOURS", "Endless mastery late-night pack", "Unlock: Endless mastery PRO"),
    "Trial Chrome": ThemePreset("TRIAL CHROME", "Challenge mastery steel-magenta pack", "Unlock: Challenge mastery PRO"),
}


DISTRICT_MODIFIERS: dict[str, DistrictModifier] = {
    "Neon Calm": DistrictModifier("NEON CALM", "Balanced district flow", colors.SKYBLUE),
    "Overdrive": DistrictModifier(
        "OVERDRIVE",
        "Faster ghost pressure",
        colors.RED,
        chase_bonus=18,
        scatter_penalty=8,
        release_bonus=2,
        ghost_score_bonus=50,
    ),
    "Power Surge": DistrictModifier(
        "POWER SURGE",
        "Longer rage, stronger seeds",
        colors.MAGENTA,
        rage_bonus=70,
        large_seed_bonus=25,
        seed_score_bonus=5,
    ),
    "Harvest Grid": DistrictModifier(
        "HARVEST GRID",
        "Faster cherries, richer route rewards",
        colors.GOLD,
        cherry_respawn_bonus=28,
        cherry_score_bonus=150,
        seed_score_bonus=5,
    ),
    "Blackout": DistrictModifier(
        "BLACKOUT",
        "Short windows, big danger",
        colors.VIOLET,
        chase_bonus=24,
        scatter_penalty=12,
        release_bonus=3,
        rage_bonus=-40,
        ghost_score_bonus=100,
    ),
}

MAP_TRAITS: dict[int, MapTrait] = {
    1: MapTrait("TRANSIT GRID", "faster cherries, steadier flow", colors.SKYBLUE, cherry_respawn_bonus=-18, cherry_score_bonus=50),
    2: MapTrait("PRESSURE LANES", "faster release, shorter scatter", colors.RED, release_bonus=2, scatter_penalty=6, chase_bonus=8),
    3: MapTrait("BLACK CHANNEL", "big risk, bigger ghost payouts", colors.VIOLET, rage_bonus=-25, ghost_score_bonus=120, chase_bonus=10),
    4: MapTrait("MARKET LOOP", "warmer bonus tempo", colors.GOLD, cherry_respawn_bonus=-24, cherry_score_bonus=100),
    5: MapTrait("CREDIT SPIRAL", "high pressure survival board", colors.MAGENTA, release_bonus=3, scatter_penalty=8, chase_bonus=14),
}


ACHIEVEMENT_DEFS: tuple[tuple[str, str, callable], ...] = (
    ("FIRST CREDIT", "Start your first run", lambda p: p["total_runs"] >= 1),
    ("STREET SWEEPER", "Eat 250 dots", lambda p: p["total_dots_eaten"] >= 250),
    ("OVERCHARGED", "Trigger 25 power seeds", lambda p: p["total_power_seeds"] >= 25),
    ("GHOST HUNTER", "Eat 25 ghosts", lambda p: p["total_ghosts_eaten"] >= 25),
    ("HI-SCORE", "Reach 5000 points", lambda p: p["best_score"] >= 5000),
    ("DISTRICT CLEAR", "Reach level 3", lambda p: p["highest_level"] >= 3),
    ("ARCADE REGULAR", "Win 3 full runs", lambda p: p["total_wins"] >= 3),
    ("ENDLESS MINDSET", "Start 3 Endless runs", lambda p: int(p.get("mode_runs", {}).get("Endless", 0)) >= 3),
    ("ONE-LIFE DISTRICT", "Win a Challenge run", lambda p: p["total_wins"] >= 1 and int(p.get("mode_runs", {}).get("Challenge", 0)) >= 1),
    ("TRIAL BOARD", "Start 5 Challenge runs", lambda p: int(p.get("mode_runs", {}).get("Challenge", 0)) >= 5),
)

RANK_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (1200, "NIGHT RUNNER"),
    (3500, "ARCADE HUNTER"),
    (7000, "DISTRICT ACE"),
    (12000, "NEON LEGEND"),
)

MODE_MASTERY_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (3, "INITIATE"),
    (9, "PRO"),
    (18, "ELITE"),
    (30, "MASTER"),
)

CHALLENGE_TRACK_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (3, "SCOUT"),
    (9, "RUNNER"),
    (18, "HUNTER"),
    (30, "TRIAL MASTER"),
)


@dataclass
class Config:
    # Display & Map
    fps: int = 16
    layout_name: str = DEFAULT_LAYOUT
    tile_size: int = 20
    map_width: int = 28
    map_height: int = 30
    hud_mode: str = "side"
    hud_extent: int = 250
    menu_button_width: int = 220
    menu_button_height: int = 56
    menu_title_size: int = 64
    menu_heading_size: int = 26
    menu_body_size: int = 20
    menu_footer_size: int = 18
    hud_font_size: int = 22
    hud_line_height: int = 28
    hud_columns: int = 1

    # Game Speed & Timing
    logic_tick_rate: int = 3
    death_animation_fps: int = 1
    rage_duration_ticks: int = 300
    cherry_respawn_ticks: int = 150
    ghost_chase_ticks: int = 120
    ghost_scatter_ticks: int = 40
    ghost_chase_tick_step: int = 10
    ghost_scatter_tick_step: int = 5
    ghost_scatter_tick_min: int = 10
    rage_duration_tick_step: int = 25
    rage_duration_tick_min: int = 120
    cherry_respawn_tick_step: int = 10
    cherry_respawn_tick_min: int = 45
    cherry_score_step: int = 100
    large_seed_score_step: int = 25
    ready_duration_ticks: int = 45
    death_pause_ticks: int = 24
    game_over_pause_ticks: int = 36
    level_complete_duration_ticks: int = 30
    ghost_release_tick_interval: int = 18
    ghost_release_tick_step: int = 2
    ghost_release_tick_min: int = 6
    ghost_fright_release_stall_ticks: int = 10

    # Score Values
    seed_score: int = 10
    large_seed_score: int = 50
    cherry_score: int = 500
    ghost_score: int = 200

    # Game State
    initial_lives: int = 3

    @property
    def board_width(self) -> int:
        return self.map_width * self.tile_size

    @property
    def board_height(self) -> int:
        return self.map_height * self.tile_size

    @property
    def board_gap(self) -> int:
        return 56 if self.layout_name == "desktop" and self.hud_mode == "side" else 0

    @property
    def board_offset_x(self) -> int:
        return 72 if self.layout_name == "desktop" and self.hud_mode == "side" else 0

    @property
    def board_offset_y(self) -> int:
        return 60 if self.layout_name == "desktop" else 0

    @property
    def window_width(self) -> int:
        if self.hud_mode == "side":
            return self.board_offset_x * 2 + self.board_width + self.board_gap + self.hud_extent
        return self.board_width

    @property
    def window_height(self) -> int:
        if self.hud_mode == "bottom":
            return self.board_height + self.hud_extent
        return self.board_height + self.board_offset_y * 2

    @property
    def hud_x(self) -> int:
        if self.hud_mode == "side":
            return self.board_offset_x + self.board_width + self.board_gap
        return 0

    @property
    def hud_y(self) -> int:
        if self.hud_mode == "bottom":
            return self.board_height
        return self.board_offset_y

    @property
    def hud_width(self) -> int:
        if self.hud_mode == "side":
            return self.hud_extent
        return self.board_width

    @property
    def hud_height(self) -> int:
        if self.hud_mode == "bottom":
            return self.hud_extent
        return self.board_height


@dataclass
class GameContext:
    cfg: Config = field(default_factory=Config)

    difficulty: str = "Normal"
    game_mode: str = "Arcade"
    challenge_name: str = "One Life District"
    score: int = 0
    high_score: int = field(default_factory=load_high_score)
    lives: int = field(default=3)
    current_level: int = 1
    last_result: str = ""
    should_resume_game: bool = False
    ghost_mode: str = "chase"
    ghost_mode_timer: int = 0
    ghost_combo: int = 0
    pressure_stage: int = 0
    visual_time: float = 0.0

    # Visual effects systems
    particles: ParticleSystem = field(default_factory=ParticleSystem)
    screen_shake: ScreenShake = field(default_factory=ScreenShake)
    floating_text: FloatingTextSystem = field(
        default_factory=FloatingTextSystem)
    screen_flash: ScreenFlash = field(default_factory=ScreenFlash)

    pacman: Optional[object] = None
    game_map: Optional[object] = None
    audio_manager: Optional[object] = None
    profile: dict = field(default_factory=load_profile)
    run_stats: RunStats = field(default_factory=RunStats)
    pre_run_unlock_snapshot: dict = field(default_factory=dict)
    last_unlock_lines: tuple[str, str, str] = field(default_factory=lambda: ("", "", ""))

    def __post_init__(self):
        self.apply_layout(self.cfg.layout_name)
        # Initialize lives from config if not already set
        if self.lives == 3:
            self.lives = self.cfg.initial_lives

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
        self.should_resume_game = False
        self.reset_ghost_mode_cycle()
        self.reset_ghost_combo()
        self.pacman = None
        self.game_map = None
        self.run_stats = RunStats()
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
        return False

    def challenge_entries(self) -> list[tuple[str, ChallengePreset, bool]]:
        return [
            (name, preset, self.challenge_unlocked(name))
            for name, preset in CHALLENGE_PRESETS.items()
        ]

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
            if self.current_level == 1:
                return RunDirective("CLEAN SWEEP", "eat 2 power seeds", "power_seeds", 2, 300, colors.MAGENTA)
            if self.current_level == 2:
                return RunDirective("NIGHT MARKET", "collect 1 cherry", "cherries", 1, 450, colors.GOLD)
            return RunDirective("GHOST BREAK", "eat 3 ghosts", "ghosts", 3, 700, colors.RED)

        if self.game_mode == "Endless":
            cycle = self.current_level % 3
            if cycle == 1:
                return RunDirective("HARVEST RUN", "earn 1800 score", "score", 1800 + max(0, self.current_level - 1) * 120, 400, colors.GOLD)
            if cycle == 2:
                return RunDirective("VOLTAGE CHAIN", "eat 4 ghosts", "ghosts", 4, 650, colors.SKYBLUE)
            return RunDirective("LUCK RUSH", "collect 1 cherry", "cherries", 1, 500, colors.GREEN)

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
        name = str(self.profile["settings"].get("theme_name", "Neon District"))
        if name not in THEME_PRESETS:
            return "Neon District"
        return name

    def set_theme_name(self, name: str) -> None:
        if name not in THEME_PRESETS or not self.theme_unlocked(name):
            return
        self.profile["settings"]["theme_name"] = name
        self.save_profile()

    def theme_unlocked(self, name: str) -> bool:
        if name == "Neon District":
            return True
        if name == "Amber Rain":
            return self.profile["total_wins"] >= 1
        if name == "Ice Circuit":
            return self.challenge_reward_count() >= 2
        if name == "Velvet Alley":
            return self.profile["best_score"] >= 5000
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

    def mode_score_multiplier(self) -> float:
        if self.game_mode == "Challenge":
            return 1.4
        if self.game_mode == "Endless":
            return min(1.35, 1.1 + max(0, self.current_level - 1) * 0.05)
        return 1.0

    def mode_pressure_bonus(self) -> int:
        if self.game_mode == "Challenge":
            return 2
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
        if self.game_mode == "Endless":
            return 250 * self.current_level
        return 400 * self.current_level

    def total_levels_for_mode(self, game_mode: Optional[str] = None) -> Optional[int]:
        return self.game_mode_preset(game_mode).max_levels

    def mode_label(self) -> str:
        return self.game_mode_preset().title

    def mode_subtitle(self) -> str:
        if self.game_mode == "Challenge":
            return self.challenge_preset().title
        return self.game_mode_preset().subtitle.upper()

    def district_modifier_name(self) -> str:
        if self.game_mode == "Challenge":
            challenge_mods = {
                "One Life District": "Blackout",
                "Score Rush": "Harvest Grid",
                "Ghost Hunt": "Overdrive",
                "Neon Sprint": "Harvest Grid",
                "Phantom Debt": "Power Surge",
                "District Ace": "Blackout",
            }
            return challenge_mods.get(self.challenge_name, "Blackout")

        if self.game_mode == "Endless":
            cycle = ("Neon Calm", "Harvest Grid", "Overdrive", "Power Surge")
            return cycle[(max(1, self.current_level) - 1) % len(cycle)]

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

    def next_ghost_combo_score(self) -> int:
        combo_step = min(self.ghost_combo, 3)
        base_score = self.cfg.ghost_score + self.district_modifier().ghost_score_bonus + self.current_map_trait().ghost_score_bonus
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
        return max(
            self.cfg.ghost_release_tick_min,
            self.cfg.ghost_release_tick_interval - level_offset * self.cfg.ghost_release_tick_step - modifier.release_bonus - map_trait.release_bonus,
        )

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
        self.current_level += 1
        if self.game_mode_preset().reset_lives_each_level:
            self.lives = self.starting_lives()
        self.mark_level_baseline()

    def record_dot_eaten(self) -> None:
        self.run_stats.dots_eaten += 1

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
        save_profile(self.profile)

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

    def new_unlock_lines(self, before: Optional[dict] = None) -> tuple[str, str, str]:
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

        new_challenges = sorted(after["challenges"] - before.get("challenges", set()))
        for name in new_challenges:
            lines.append(f"Trial Unlocked: {CHALLENGE_PRESETS[name].title}")

        new_achievements = sorted(after["achievements"] - before.get("achievements", set()))
        for title in new_achievements:
            lines.append(f"Achievement: {title}")

        new_rewards = sorted(after["challenge_rewards"] - before.get("challenge_rewards", set()))
        for name in new_rewards:
            lines.append(f"Trophy Earned: {CHALLENGE_PRESETS[name].reward_title}")

        if not lines:
            next_goals = [line for line in self.career_goal_lines() if line]
            while len(next_goals) < 3:
                next_goals.append("Keep pushing the district")
            return (next_goals[0], next_goals[1], next_goals[2])

        while len(lines) < 3:
            lines.append("More unlocks waiting in Career")
        return (lines[0], lines[1], lines[2])

    def fx_intensity(self) -> str:
        return str(self.profile["settings"].get("fx_intensity", "High"))

    def set_fx_intensity(self, value: str) -> None:
        if value not in {"Low", "Medium", "High"}:
            return
        self.profile["settings"]["fx_intensity"] = value
        self.save_profile()

    def screen_flash_enabled(self) -> bool:
        return bool(self.profile["settings"].get("screen_flash", 1))

    def set_screen_flash_enabled(self, enabled: bool) -> None:
        self.profile["settings"]["screen_flash"] = 1 if enabled else 0
        self.save_profile()

    def screen_shake_enabled(self) -> bool:
        return bool(self.profile["settings"].get("screen_shake", 1))

    def set_screen_shake_enabled(self, enabled: bool) -> None:
        self.profile["settings"]["screen_shake"] = 1 if enabled else 0
        self.save_profile()

    def music_enabled(self) -> bool:
        return bool(self.profile["settings"].get("music_enabled", 1))

    def set_music_enabled(self, enabled: bool) -> None:
        self.profile["settings"]["music_enabled"] = 1 if enabled else 0
        self.save_profile()

    def sfx_enabled(self) -> bool:
        return bool(self.profile["settings"].get("sfx_enabled", 1))

    def set_sfx_enabled(self, enabled: bool) -> None:
        self.profile["settings"]["sfx_enabled"] = 1 if enabled else 0
        self.save_profile()

    def tutorial_enabled(self) -> bool:
        return bool(self.profile["settings"].get("tutorial_enabled", 1))

    def set_tutorial_enabled(self, enabled: bool) -> None:
        self.profile["settings"]["tutorial_enabled"] = 1 if enabled else 0
        self.save_profile()

    def tutorial_seen(self) -> bool:
        return bool(self.profile.get("tutorial_seen", 0))

    def mark_tutorial_seen(self) -> None:
        self.profile["tutorial_seen"] = 1
        self.save_profile()

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
            f"Challenge {self.mode_mastery_rank('Challenge')} {self.mode_mastery_value('Challenge')}",
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
            f"Arcade Runs {int(mode_runs.get('Arcade', 0))}",
            f"Endless Runs {int(mode_runs.get('Endless', 0))}",
            f"Challenge Runs {int(mode_runs.get('Challenge', 0))}",
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
