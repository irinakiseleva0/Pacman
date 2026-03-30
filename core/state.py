from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from utils.score_storage import load_high_score
from utils.visual_effects import FloatingTextSystem, LightBurstSystem, ParticleSystem, ScreenFlash, ScreenShake


@dataclass
class RunStats:
    dots_eaten: int = 0
    power_seeds_eaten: int = 0
    cherries_eaten: int = 0
    ghosts_eaten: int = 0
    near_misses: int = 0
    thread_turns: int = 0
    line_bonuses: int = 0
    levels_cleared: int = 0
    level_start_score: int = 0
    level_start_dots: int = 0
    level_start_power_seeds: int = 0
    level_start_cherries: int = 0
    level_start_ghosts: int = 0
    finalized: bool = False


@dataclass
class RunState:
    difficulty: str = "Normal"
    game_mode: str = "Arcade"
    challenge_name: str = "One Life District"
    score: int = 0
    high_score: int = field(default_factory=load_high_score)
    lives: int = 3
    current_level: int = 1
    last_result: str = ""
    should_resume_game: bool = False
    ghost_mode: str = "chase"
    ghost_mode_timer: int = 0
    ghost_combo: int = 0
    power_chain_level: int = 0
    power_chain_window: int = 0
    route_chain_count: int = 0
    route_chain_window: int = 0
    line_chain_count: int = 0
    line_chain_dx: int = 0
    line_chain_dy: int = 0
    pressure_stage: int = 0
    time_attack_seconds: float = 0.0
    last_killer_name: str = ""


@dataclass
class RuntimeRefs:
    pacman: Optional[object] = None
    game_map: Optional[object] = None
    audio_manager: Optional[object] = None


@dataclass
class VisualSystems:
    particles: ParticleSystem = field(default_factory=ParticleSystem)
    light_bursts: LightBurstSystem = field(default_factory=LightBurstSystem)
    screen_shake: ScreenShake = field(default_factory=ScreenShake)
    floating_text: FloatingTextSystem = field(default_factory=FloatingTextSystem)
    screen_flash: ScreenFlash = field(default_factory=ScreenFlash)
    visual_time: float = 0.0
