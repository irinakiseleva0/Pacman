from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from utils.profile_storage import load_profile
from utils.visual_effects import FloatingTextSystem, ParticleSystem, ScreenFlash, ScreenShake


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


@dataclass
class VisualSystems:
    particles: ParticleSystem = field(default_factory=ParticleSystem)
    screen_shake: ScreenShake = field(default_factory=ScreenShake)
    floating_text: FloatingTextSystem = field(default_factory=FloatingTextSystem)
    screen_flash: ScreenFlash = field(default_factory=ScreenFlash)
    visual_time: float = 0.0


@dataclass
class RuntimeRefs:
    pacman: Optional[object] = None
    game_map: Optional[object] = None
    audio_manager: Optional[object] = None


@dataclass
class ProgressionState:
    profile: dict = field(default_factory=load_profile)
    run_stats: RunStats = field(default_factory=RunStats)
    pre_run_unlock_snapshot: dict = field(default_factory=dict)
    last_unlock_lines: tuple[str, str, str] = field(default_factory=lambda: ("", "", ""))
    last_unlocks_are_new: bool = False
