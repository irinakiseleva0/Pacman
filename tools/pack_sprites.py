from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.logger import get_logger, setup_logging


TILE_W = 16
TILE_H = 16
COLS = 16
OUTPUT_DIR = Path("assets/sprites")
OUTPUT_ATLAS = OUTPUT_DIR / "atlas.png"
OUTPUT_MAP = OUTPUT_DIR / "atlas_map.json"


log = get_logger(__name__)


def _input_dir(name: str) -> Path:
    preferred = Path("assets/sprites") / name
    fallback = Path("sprites") / name
    return preferred if preferred.exists() else fallback


def _load_frame(path: Path) -> pygame.Surface:
    surface = pygame.image.load(str(path))
    if surface.get_flags() & pygame.SRCALPHA:
        return surface.copy()
    return surface.convert_alpha() if pygame.display.get_surface() is not None else surface.convert(32, pygame.SRCALPHA)


def _add(mapping: dict[str, Path], key: str, path: Path) -> None:
    if path.exists():
        mapping[key] = path


def collect_frames() -> dict[str, Path]:
    frames: dict[str, Path] = {}
    pacman_dir = _input_dir("pacman")
    ghost_dir = _input_dir("ghosts")

    pacman_directions = {
        "right": "right",
        "left": "left",
        "up": "up",
        "down": "down",
    }
    for direction, suffix in pacman_directions.items():
        for frame in range(2):
            _add(frames, f"pacman_{direction}_{frame}", pacman_dir / f"pacman_pos_{frame + 1}_{suffix}.png")
    for frame in range(10):
        _add(frames, f"pacman_death_{frame}", pacman_dir / "death" / f"death_{frame + 1}.png")

    for ghost_name in ("red", "magenta", "cyan", "orange"):
        for direction in ("right", "left", "up", "down"):
            for frame in range(2):
                _add(
                    frames,
                    f"ghost_{ghost_name}_{direction}_{frame}",
                    ghost_dir / ghost_name / f"{ghost_name}_ghost_pos_{frame + 1}_{direction}.png",
                )

    for direction in ("right", "left", "up", "down"):
        for frame in range(2):
            _add(frames, f"ghost_weak_{direction}_{frame}", ghost_dir / "weak" / f"weak_ghost_pos_{frame + 1}.png")

    return frames


def pack() -> None:
    setup_logging()
    pygame.init()
    frames = collect_frames()
    if not frames:
        raise SystemExit("No sprite PNG files found in assets/sprites or sprites.")

    rows = math.ceil(len(frames) / COLS)
    atlas = pygame.Surface((COLS * TILE_W, rows * TILE_H), pygame.SRCALPHA)
    atlas.fill((0, 0, 0, 0))

    atlas_map: dict[str, int] = {}
    for index, (key, path) in enumerate(frames.items()):
        frame = _load_frame(path)
        if frame.get_size() != (TILE_W, TILE_H):
            frame = pygame.transform.scale(frame, (TILE_W, TILE_H))
        x = (index % COLS) * TILE_W
        y = (index // COLS) * TILE_H
        atlas.blit(frame, (x, y))
        atlas_map[key] = index

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pygame.image.save(atlas, str(OUTPUT_ATLAS))
    OUTPUT_MAP.write_text(json.dumps(atlas_map, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log.info("Packed %s sprites into %s", len(atlas_map), OUTPUT_ATLAS)
    log.info("Wrote %s", OUTPUT_MAP)


if __name__ == "__main__":
    pack()
