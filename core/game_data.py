from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from raylib import colors


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
    board_tag: str
    threat_label: str
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
class HudPackPreset:
    title: str
    subtitle: str
    unlock_text: str


@dataclass(frozen=True)
class TitleVariantPreset:
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
class ArcadeChapter:
    title: str
    subtitle: str
    briefing: str
    accent: tuple[int, int, int, int]


@dataclass(frozen=True)
class EndlessTier:
    title: str
    subtitle: str
    accent: tuple[int, int, int, int]
    clear_bonus: int


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
    "Time Attack": GameModePreset(
        title="TIME ATTACK",
        subtitle="Beat the district clock",
        summary_lines=(
            "Race through three timed districts",
            "Bank seconds on every successful clear",
            "Built for tempo routes and fast recovery",
        ),
        accent=colors.ORANGE,
        max_levels=3,
        map_cycle=(4, 2, 5),
        reset_lives_each_level=True,
    ),
}


CHALLENGE_PRESETS: dict[str, ChallengePreset] = {
    "One Life District": ChallengePreset("ONE LIFE", "Clear the district with one life", ("Drops you into the hardest district", "One life only, no refresh, no excuses", "Clear the board to complete the trial"), colors.MAGENTA, (3,), 1, "BOARD A1", "SURVIVAL", unlock_text="Available from the start", reward_title="ONE LIFE SIGIL"),
    "Score Rush": ChallengePreset("SCORE RUSH", "Clear and finish above 3200", ("Clear District 2 with a score target", "Need 3200 points or more at the finish", "High pressure route-planning challenge"), colors.GOLD, (2,), 2, "BOARD B2", "SCORE", target_score=3200, unlock_text="Unlock: finish 3 total runs", reward_title="RUSH CIRCUIT"),
    "Ghost Hunt": ChallengePreset("GHOST HUNT", "Clear and eat 4 ghosts", ("Play the hard district with 2 lives", "You must eat at least 4 ghosts in-run", "Balance survival with aggressive routing"), colors.SKYBLUE, (3,), 2, "BOARD C1", "HUNT", target_ghosts=4, unlock_text="Unlock: eat 10 ghosts total", reward_title="HUNTER EMBLEM"),
    "Neon Sprint": ChallengePreset("NEON SPRINT", "Clear District 1 above 1800", ("Fast clear on the opening district", "You need 1800 score by board clear", "Built around clean routing and tempo"), colors.GREEN, (4,), 2, "BOARD A2", "ROUTE", target_score=1800, unlock_text="Unlock: reach level 2", reward_title="SPRINT STRIP"),
    "Phantom Debt": ChallengePreset("PHANTOM DEBT", "One life, eat 6 ghosts", ("Single-life pressure on District 2", "Need to eat 6 ghosts before the clear", "Demands brave power-seed routing"), colors.ORANGE, (2,), 1, "BOARD C3", "RISK", target_ghosts=6, unlock_text="Unlock: win 1 run", reward_title="PHANTOM MARK"),
    "District Ace": ChallengePreset("DISTRICT ACE", "Clear District 3 above 4200", ("Late-district prestige score challenge", "Reach 4200 by the end of the clear", "The harshest score target in the board"), colors.VIOLET, (3,), 2, "BOARD D1", "PRESTIGE", target_score=4200, unlock_text="Unlock: best score 3500", reward_title="ACE CREST"),
    "Midnight Relay": ChallengePreset("MIDNIGHT RELAY", "Clear District 1 and eat 3 ghosts", ("Compact opening-district relay trial", "Need 3 ghost eats before the clear", "Short route, fast commitment"), colors.BLUE, (4,), 2, "BOARD B1", "CHAIN", target_ghosts=3, unlock_text="Unlock: clear 1 level", reward_title="RELAY BAND"),
    "Credit Burner": ChallengePreset("CREDIT BURNER", "One life, clear above 2600", ("One-life score run on District 2", "Need 2600 points by board clear", "A clean route with no panic deaths"), colors.YELLOW, (5,), 1, "BOARD C2", "SCORE", target_score=2600, unlock_text="Unlock: total score 2000", reward_title="BURNER CHIP"),
    "Last Call": ChallengePreset("LAST CALL", "Clear District 3 and eat 8 ghosts", ("Late-board ghost pressure challenge", "Eat 8 ghosts before the district ends", "Built for long power-chain routing"), colors.PINK, (3,), 2, "BOARD D2", "HUNT", target_ghosts=8, unlock_text="Unlock: eat 20 ghosts total", reward_title="LAST CALL PASS"),
    "Redline Protocol": ChallengePreset("REDLINE EX", "Elite district clear above 5200", ("Prestige board with elite pressure", "Finish above 5200 on the final district", "Built for top-rank score routing"), colors.RED, (5,), 2, "BOARD E1", "ELITE", target_score=5200, unlock_text="Unlock: Challenge rank HUNTER", reward_title="REDLINE CORE"),
    "Clock Reaper": ChallengePreset("CLOCK REAPER", "Timed hunt, clear and eat 7 ghosts", ("Tempo-heavy hunt on a timed board", "Eat 7 ghosts before the district falls", "Designed for high-pressure chain play"), colors.ORANGE, (4,), 1, "BOARD E2", "ELITE", target_ghosts=7, unlock_text="Unlock: Time Attack mastery PRO", reward_title="REAPER CLOCK"),
}

THEME_PRESETS: dict[str, ThemePreset] = {
    "Neon District": ThemePreset("NEON DISTRICT", "Classic cyan-magenta night", "Available from the start"),
    "Amber Rain": ThemePreset("AMBER RAIN", "Warm gold rain-soaked signage", "Unlock: win 1 run"),
    "Ice Circuit": ThemePreset("ICE CIRCUIT", "Cold cyan and steel palette", "Unlock: 2 trial trophies"),
    "Velvet Alley": ThemePreset("VELVET ALLEY", "Magenta-heavy moody street look", "Unlock: best score 5000"),
    "Cool Summer": ThemePreset("COOL SUMMER", "Soft blue-violet neon summer night", "Unlock: clear 3 total levels"),
    "Solar Pulse": ThemePreset("SOLAR PULSE", "Yellow-orange signal heat", "Unlock: best score 4200"),
    "Ultraviolet": ThemePreset("ULTRAVIOLET", "Deep purple-blue afterglow pack", "Unlock: 6 trial trophies"),
    "Grid Echo": ThemePreset("GRID ECHO", "Arcade mastery cyan-grid pack", "Unlock: Arcade mastery PRO"),
    "After Hours": ThemePreset("AFTER HOURS", "Endless mastery late-night pack", "Unlock: Endless mastery PRO"),
    "Trial Chrome": ThemePreset("TRIAL CHROME", "Challenge mastery steel-magenta pack", "Unlock: Challenge mastery PRO"),
}

HUD_PACK_PRESETS: dict[str, HudPackPreset] = {
    "Standard": HudPackPreset("STANDARD", "Balanced district HUD", "Available from the start"),
    "Relay Grid": HudPackPreset("RELAY GRID", "Route-first broadcast layout", "Unlock: reach Arcade mastery 9"),
    "Hunter Scope": HudPackPreset("HUNTER SCOPE", "Aggressive ghost-tracking layout", "Unlock: earn 4 challenge trophies"),
    "Chrome Vector": HudPackPreset("CHROME VECTOR", "High-end operator telemetry", "Unlock: reach best score 6500"),
}

TITLE_VARIANT_PRESETS: dict[str, TitleVariantPreset] = {
    "Standard": TitleVariantPreset("STANDARD", "Clean cinematic stack", "Available from the start"),
    "Broadcast": TitleVariantPreset("BROADCAST", "Wide scanline title treatment", "Unlock: win 2 runs"),
    "Splitline": TitleVariantPreset("SPLITLINE", "Sharp tempo-led title module", "Unlock: Time Attack mastery PRO"),
    "Executive": TitleVariantPreset("EXECUTIVE", "Prestige premium title frame", "Unlock: best score 7000"),
}

DISTRICT_MODIFIERS: dict[str, DistrictModifier] = {
    "Neon Calm": DistrictModifier("NEON CALM", "Balanced district flow", colors.SKYBLUE),
    "Overdrive": DistrictModifier("OVERDRIVE", "Faster ghost pressure", colors.RED, chase_bonus=18, scatter_penalty=8, release_bonus=2, ghost_score_bonus=50),
    "Power Surge": DistrictModifier("POWER SURGE", "Longer rage, stronger seeds", colors.MAGENTA, rage_bonus=70, large_seed_bonus=25, seed_score_bonus=5),
    "Harvest Grid": DistrictModifier("HARVEST GRID", "Faster cherries, richer route rewards", colors.GOLD, cherry_respawn_bonus=28, cherry_score_bonus=150, seed_score_bonus=5),
    "Blackout": DistrictModifier("BLACKOUT", "Short windows, big danger", colors.VIOLET, chase_bonus=24, scatter_penalty=12, release_bonus=3, rage_bonus=-40, ghost_score_bonus=100),
    "Redline Sector": DistrictModifier("REDLINE SECTOR", "Elite overrun district", colors.RED, chase_bonus=32, scatter_penalty=16, release_bonus=4, ghost_score_bonus=160, seed_score_bonus=8),
    "Null Pulse": DistrictModifier("NULL PULSE", "Cold precision and short windows", colors.SKYBLUE, chase_bonus=18, scatter_penalty=10, release_bonus=3, rage_bonus=-28, cherry_score_bonus=220),
}

MAP_TRAITS: dict[int, MapTrait] = {
    1: MapTrait("TRANSIT GRID", "faster cherries, steadier flow", colors.SKYBLUE, cherry_respawn_bonus=-18, cherry_score_bonus=50),
    2: MapTrait("PRESSURE LANES", "faster release, shorter scatter", colors.RED, release_bonus=2, scatter_penalty=6, chase_bonus=8),
    3: MapTrait("BLACK CHANNEL", "big risk, bigger ghost payouts", colors.VIOLET, rage_bonus=-25, ghost_score_bonus=120, chase_bonus=10),
    4: MapTrait("MARKET LOOP", "warmer bonus tempo", colors.GOLD, cherry_respawn_bonus=-24, cherry_score_bonus=100),
    5: MapTrait("CREDIT SPIRAL", "high pressure survival board", colors.MAGENTA, release_bonus=3, scatter_penalty=8, chase_bonus=14),
}

ARCADE_CHAPTERS: tuple[ArcadeChapter, ...] = (
    ArcadeChapter("CHAPTER 01", "TRANSIT GATE", "secure the district and establish tempo", colors.SKYBLUE),
    ArcadeChapter("CHAPTER 02", "NIGHT MARKET", "push bonus routes through the warm loop", colors.GOLD),
    ArcadeChapter("CHAPTER 03", "CREDIT SPIRAL", "survive the final pressure district", colors.MAGENTA),
)

ENDLESS_TIERS: tuple[tuple[int, EndlessTier], ...] = (
    (1, EndlessTier("SURVIVAL TIER 1", "district drift", colors.SKYBLUE, 250)),
    (3, EndlessTier("SURVIVAL TIER 2", "pressure climb", colors.GOLD, 360)),
    (5, EndlessTier("SURVIVAL TIER 3", "overrun lanes", colors.ORANGE, 500)),
    (7, EndlessTier("SURVIVAL TIER 4", "after hours collapse", colors.RED, 650)),
)

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
