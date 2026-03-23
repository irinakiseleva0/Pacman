from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from utils.score_storage import load_high_score
from utils.visual_effects import ParticleSystem, ScreenShake, FloatingTextSystem, ScreenFlash


@dataclass(frozen=True)
class DifficultyPreset:
    logic_tick_rate: int
    rage_duration_ticks: int
    cherry_respawn_ticks: int
    ghost_chase_ticks: int
    ghost_scatter_ticks: int
    initial_lives: int
    seed_score: int
    large_seed_score: int
    cherry_score: int
    ghost_score: int
    summary_lines: tuple[str, str, str]


DIFFICULTY_PRESETS: dict[str, DifficultyPreset] = {
    "Easy": DifficultyPreset(
        logic_tick_rate=2,
        rage_duration_ticks=450,
        cherry_respawn_ticks=200,
        ghost_chase_ticks=90,
        ghost_scatter_ticks=70,
        initial_lives=5,
        seed_score=15,
        large_seed_score=75,
        cherry_score=750,
        ghost_score=300,
        summary_lines=(
            "Lives: 5  Rage: long",
            "Ghosts: lighter pressure",
            "Score: generous rewards",
        ),
    ),
    "Normal": DifficultyPreset(
        logic_tick_rate=3,
        rage_duration_ticks=300,
        cherry_respawn_ticks=150,
        ghost_chase_ticks=120,
        ghost_scatter_ticks=40,
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
        initial_lives=2,
        seed_score=5,
        large_seed_score=25,
        cherry_score=250,
        ghost_score=100,
        summary_lines=(
            "Lives: 2  Rage: short",
            "Ghosts: aggressive pressure",
            "Score: reduced rewards",
        ),
    ),
}


@dataclass
class Config:
    # Display & Map
    fps: int = 16
    tile_size: int = 16
    map_width: int = 28
    map_height: int = 30

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
    ready_duration_ticks: int = 45
    level_complete_duration_ticks: int = 30

    # Score Values
    seed_score: int = 10
    large_seed_score: int = 50
    cherry_score: int = 500
    ghost_score: int = 200

    # Game State
    initial_lives: int = 3

    @property
    def window_width(self) -> int:
        return self.map_width * self.tile_size

    @property
    def window_height(self) -> int:
        return self.map_height * self.tile_size


@dataclass
class GameContext:
    cfg: Config = field(default_factory=Config)

    difficulty: str = "Normal"
    score: int = 0
    high_score: int = field(default_factory=load_high_score)
    lives: int = field(default=3)
    current_level: int = 1
    last_result: str = ""
    should_resume_game: bool = False
    ghost_mode: str = "chase"
    ghost_mode_timer: int = 0
    ghost_combo: int = 0

    # Visual effects systems
    particles: ParticleSystem = field(default_factory=ParticleSystem)
    screen_shake: ScreenShake = field(default_factory=ScreenShake)
    floating_text: FloatingTextSystem = field(
        default_factory=FloatingTextSystem)
    screen_flash: ScreenFlash = field(default_factory=ScreenFlash)

    pacman: Optional[object] = None
    game_map: Optional[object] = None

    def __post_init__(self):
        # Initialize lives from config if not already set
        if self.lives == 3:
            self.lives = self.cfg.initial_lives

    def reset_run_state(self) -> None:
        """Reset progress for a fresh run without touching persistent data."""
        self.score = 0
        self.lives = self.cfg.initial_lives
        self.current_level = 1
        self.last_result = ""
        self.should_resume_game = False
        self.reset_ghost_mode_cycle()
        self.reset_ghost_combo()
        self.pacman = None
        self.game_map = None

    def start_new_game(self) -> None:
        """Start a new game using the current config."""
        self.reset_run_state()

    def apply_difficulty(self, difficulty: str) -> None:
        preset = DIFFICULTY_PRESETS[difficulty]
        self.difficulty = difficulty

        self.cfg.logic_tick_rate = preset.logic_tick_rate
        self.cfg.rage_duration_ticks = preset.rage_duration_ticks
        self.cfg.cherry_respawn_ticks = preset.cherry_respawn_ticks
        self.cfg.ghost_chase_ticks = preset.ghost_chase_ticks
        self.cfg.ghost_scatter_ticks = preset.ghost_scatter_ticks
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

    def reset_ghost_combo(self) -> None:
        self.ghost_combo = 0

    def next_ghost_combo_score(self) -> int:
        combo_step = min(self.ghost_combo, 3)
        return self.cfg.ghost_score * (2 ** combo_step)

    def effective_ghost_cycle(self) -> tuple[int, int]:
        level_offset = max(0, self.current_level - 1)
        chase_ticks = self.cfg.ghost_chase_ticks + level_offset * self.cfg.ghost_chase_tick_step
        scatter_ticks = max(
            self.cfg.ghost_scatter_tick_min,
            self.cfg.ghost_scatter_ticks - level_offset * self.cfg.ghost_scatter_tick_step,
        )
        return chase_ticks, scatter_ticks

    def effective_rage_duration(self) -> int:
        level_offset = max(0, self.current_level - 1)
        return max(
            self.cfg.rage_duration_tick_min,
            self.cfg.rage_duration_ticks - level_offset * self.cfg.rage_duration_tick_step,
        )

    def effective_cherry_respawn(self) -> int:
        level_offset = max(0, self.current_level - 1)
        return max(
            self.cfg.cherry_respawn_tick_min,
            self.cfg.cherry_respawn_ticks - level_offset * self.cfg.cherry_respawn_tick_step,
        )

    def effective_item_counts(self) -> tuple[int, int, int] | None:
        if self.game_map is None:
            return None
        return self.game_map.item_counts()

    def advance_ghost_mode_cycle(self) -> None:
        self.ghost_mode_timer += 1

        chase_ticks, scatter_ticks = self.effective_ghost_cycle()
        cycle_length = chase_ticks + scatter_ticks
        cycle_tick = self.ghost_mode_timer % cycle_length

        if cycle_tick < chase_ticks:
            self.ghost_mode = "chase"
        else:
            self.ghost_mode = "scatter"

    def get_map_path(self, level: Optional[int] = None) -> str:
        """Get the map file path for a given level (1-indexed)."""
        level = level or self.current_level
        if level == 1:
            return "maps/pacman_map.txt"
        return f"maps/pacman_map{level}.txt"

    def next_level(self) -> None:
        """Advance to the next level."""
        self.current_level += 1
        self.lives = self.cfg.initial_lives
