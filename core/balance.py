from __future__ import annotations

from dataclasses import dataclass


LEGACY_BALANCE_FPS = 16.0


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
class Config:
    fps: int = 60
    layout_name: str = "desktop"
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
    seed_score: int = 10
    large_seed_score: int = 50
    cherry_score: int = 500
    ghost_score: int = 200
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

    def legacy_frames_to_seconds(self, frames: int | float) -> float:
        return float(frames) / LEGACY_BALANCE_FPS

    def logic_step_seconds(self) -> float:
        return self.legacy_frames_to_seconds(self.logic_tick_rate)


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
