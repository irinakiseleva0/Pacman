from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


LEGACY_BALANCE_FPS = 16.0
_CONFIG_DIR = Path(__file__).resolve().parent.parent / "data" / "config"

_RUNTIME_FALLBACK = {
    "fps": 60,
    "layout_name": "desktop",
    "tile_size": 20,
    "map_width": 28,
    "map_height": 30,
    "hud_mode": "side",
    "hud_extent": 250,
    "menu_button_width": 220,
    "menu_button_height": 56,
    "menu_title_size": 64,
    "menu_heading_size": 26,
    "menu_body_size": 20,
    "menu_footer_size": 18,
    "hud_font_size": 22,
    "hud_line_height": 28,
    "hud_columns": 1,
    "logic_tick_rate": 3,
    "death_animation_fps": 1,
    "rage_duration_ticks": 300,
    "cherry_respawn_ticks": 150,
    "ghost_chase_ticks": 120,
    "ghost_scatter_ticks": 40,
    "ghost_chase_tick_step": 10,
    "ghost_scatter_tick_step": 5,
    "ghost_scatter_tick_min": 10,
    "rage_duration_tick_step": 25,
    "rage_duration_tick_min": 120,
    "cherry_respawn_tick_step": 10,
    "cherry_respawn_tick_min": 45,
    "cherry_score_step": 100,
    "large_seed_score_step": 25,
    "ready_duration_ticks": 45,
    "death_pause_ticks": 24,
    "game_over_pause_ticks": 36,
    "level_complete_duration_ticks": 30,
    "ghost_release_tick_interval": 18,
    "ghost_release_tick_step": 2,
    "ghost_release_tick_min": 6,
    "ghost_fright_release_stall_ticks": 10,
    "seed_score": 10,
    "large_seed_score": 50,
    "cherry_score": 500,
    "ghost_score": 200,
    "initial_lives": 3,
}

_DIFFICULTY_FALLBACK = {
    "Easy": {
        "logic_tick_rate": 2,
        "rage_duration_ticks": 450,
        "cherry_respawn_ticks": 200,
        "ghost_chase_ticks": 90,
        "ghost_scatter_ticks": 70,
        "ghost_release_tick_interval": 24,
        "initial_lives": 5,
        "seed_score": 15,
        "large_seed_score": 75,
        "cherry_score": 750,
        "ghost_score": 300,
        "summary_lines": [
            "Lives: 5  Rage: long",
            "Ghosts: lighter pressure, slower release",
            "Score: generous rewards",
        ],
    },
    "Normal": {
        "logic_tick_rate": 3,
        "rage_duration_ticks": 300,
        "cherry_respawn_ticks": 150,
        "ghost_chase_ticks": 120,
        "ghost_scatter_ticks": 40,
        "ghost_release_tick_interval": 18,
        "initial_lives": 3,
        "seed_score": 10,
        "large_seed_score": 50,
        "cherry_score": 500,
        "ghost_score": 200,
        "summary_lines": [
            "Lives: 3  Rage: standard",
            "Ghosts: balanced pressure",
            "Score: standard rewards",
        ],
    },
    "Hard": {
        "logic_tick_rate": 4,
        "rage_duration_ticks": 200,
        "cherry_respawn_ticks": 100,
        "ghost_chase_ticks": 150,
        "ghost_scatter_ticks": 25,
        "ghost_release_tick_interval": 12,
        "initial_lives": 2,
        "seed_score": 5,
        "large_seed_score": 25,
        "cherry_score": 250,
        "ghost_score": 100,
        "summary_lines": [
            "Lives: 2  Rage: short",
            "Ghosts: aggressive pressure, fast release",
            "Score: reduced rewards",
        ],
    },
}


def _load_json_config(filename: str, fallback: dict) -> dict:
    path = _CONFIG_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            merged = dict(fallback)
            merged.update(data)
            return merged
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        pass
    return dict(fallback)


_RUNTIME_DEFAULTS = _load_json_config("runtime.json", _RUNTIME_FALLBACK)
_DIFFICULTY_DEFAULTS = _load_json_config("difficulties.json", _DIFFICULTY_FALLBACK)


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
    fps: int = _RUNTIME_DEFAULTS["fps"]
    layout_name: str = _RUNTIME_DEFAULTS["layout_name"]
    tile_size: int = _RUNTIME_DEFAULTS["tile_size"]
    map_width: int = _RUNTIME_DEFAULTS["map_width"]
    map_height: int = _RUNTIME_DEFAULTS["map_height"]
    hud_mode: str = _RUNTIME_DEFAULTS["hud_mode"]
    hud_extent: int = _RUNTIME_DEFAULTS["hud_extent"]
    menu_button_width: int = _RUNTIME_DEFAULTS["menu_button_width"]
    menu_button_height: int = _RUNTIME_DEFAULTS["menu_button_height"]
    menu_title_size: int = _RUNTIME_DEFAULTS["menu_title_size"]
    menu_heading_size: int = _RUNTIME_DEFAULTS["menu_heading_size"]
    menu_body_size: int = _RUNTIME_DEFAULTS["menu_body_size"]
    menu_footer_size: int = _RUNTIME_DEFAULTS["menu_footer_size"]
    hud_font_size: int = _RUNTIME_DEFAULTS["hud_font_size"]
    hud_line_height: int = _RUNTIME_DEFAULTS["hud_line_height"]
    hud_columns: int = _RUNTIME_DEFAULTS["hud_columns"]
    logic_tick_rate: int = _RUNTIME_DEFAULTS["logic_tick_rate"]
    death_animation_fps: int = _RUNTIME_DEFAULTS["death_animation_fps"]
    rage_duration_ticks: int = _RUNTIME_DEFAULTS["rage_duration_ticks"]
    cherry_respawn_ticks: int = _RUNTIME_DEFAULTS["cherry_respawn_ticks"]
    ghost_chase_ticks: int = _RUNTIME_DEFAULTS["ghost_chase_ticks"]
    ghost_scatter_ticks: int = _RUNTIME_DEFAULTS["ghost_scatter_ticks"]
    ghost_chase_tick_step: int = _RUNTIME_DEFAULTS["ghost_chase_tick_step"]
    ghost_scatter_tick_step: int = _RUNTIME_DEFAULTS["ghost_scatter_tick_step"]
    ghost_scatter_tick_min: int = _RUNTIME_DEFAULTS["ghost_scatter_tick_min"]
    rage_duration_tick_step: int = _RUNTIME_DEFAULTS["rage_duration_tick_step"]
    rage_duration_tick_min: int = _RUNTIME_DEFAULTS["rage_duration_tick_min"]
    cherry_respawn_tick_step: int = _RUNTIME_DEFAULTS["cherry_respawn_tick_step"]
    cherry_respawn_tick_min: int = _RUNTIME_DEFAULTS["cherry_respawn_tick_min"]
    cherry_score_step: int = _RUNTIME_DEFAULTS["cherry_score_step"]
    large_seed_score_step: int = _RUNTIME_DEFAULTS["large_seed_score_step"]
    ready_duration_ticks: int = _RUNTIME_DEFAULTS["ready_duration_ticks"]
    death_pause_ticks: int = _RUNTIME_DEFAULTS["death_pause_ticks"]
    game_over_pause_ticks: int = _RUNTIME_DEFAULTS["game_over_pause_ticks"]
    level_complete_duration_ticks: int = _RUNTIME_DEFAULTS["level_complete_duration_ticks"]
    ghost_release_tick_interval: int = _RUNTIME_DEFAULTS["ghost_release_tick_interval"]
    ghost_release_tick_step: int = _RUNTIME_DEFAULTS["ghost_release_tick_step"]
    ghost_release_tick_min: int = _RUNTIME_DEFAULTS["ghost_release_tick_min"]
    ghost_fright_release_stall_ticks: int = _RUNTIME_DEFAULTS["ghost_fright_release_stall_ticks"]
    seed_score: int = _RUNTIME_DEFAULTS["seed_score"]
    large_seed_score: int = _RUNTIME_DEFAULTS["large_seed_score"]
    cherry_score: int = _RUNTIME_DEFAULTS["cherry_score"]
    ghost_score: int = _RUNTIME_DEFAULTS["ghost_score"]
    initial_lives: int = _RUNTIME_DEFAULTS["initial_lives"]

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


def _build_difficulty_presets() -> dict[str, DifficultyPreset]:
    presets: dict[str, DifficultyPreset] = {}
    for name, values in _DIFFICULTY_DEFAULTS.items():
        presets[name] = DifficultyPreset(
            logic_tick_rate=values["logic_tick_rate"],
            rage_duration_ticks=values["rage_duration_ticks"],
            cherry_respawn_ticks=values["cherry_respawn_ticks"],
            ghost_chase_ticks=values["ghost_chase_ticks"],
            ghost_scatter_ticks=values["ghost_scatter_ticks"],
            ghost_release_tick_interval=values["ghost_release_tick_interval"],
            initial_lives=values["initial_lives"],
            seed_score=values["seed_score"],
            large_seed_score=values["large_seed_score"],
            cherry_score=values["cherry_score"],
            ghost_score=values["ghost_score"],
            summary_lines=tuple(values["summary_lines"]),
        )
    return presets


DIFFICULTY_PRESETS: dict[str, DifficultyPreset] = _build_difficulty_presets()
