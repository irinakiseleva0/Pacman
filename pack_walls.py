from __future__ import annotations

import json
import math
from pathlib import Path

import pygame

from utils.logger import get_logger, setup_logging


SOURCE_DIR = Path("sprites") / "walls"
ATLAS_IMAGE = Path("sprites") / "walls_atlas.png"
ATLAS_JSON = Path("sprites") / "walls_atlas.json"
log = get_logger(__name__)


def _surface(path: Path) -> pygame.Surface:
    surface = pygame.image.load(str(path))
    try:
        return surface.convert_alpha()
    except pygame.error:
        return surface.copy()


def pack_walls() -> None:
    setup_logging()
    pygame.init()
    files = sorted(SOURCE_DIR.rglob("*.png"))
    if not files:
        raise FileNotFoundError(f"No PNG files found under {SOURCE_DIR}")

    loaded = [(path, _surface(path)) for path in files]
    cell_w = max(surface.get_width() for _path, surface in loaded)
    cell_h = max(surface.get_height() for _path, surface in loaded)
    columns = max(1, math.ceil(math.sqrt(len(loaded))))
    rows = math.ceil(len(loaded) / columns)

    atlas = pygame.Surface((columns * cell_w, rows * cell_h), pygame.SRCALPHA)
    mapping: dict[str, dict[str, int]] = {}
    for index, (path, surface) in enumerate(loaded):
        x = (index % columns) * cell_w
        y = (index // columns) * cell_h
        atlas.blit(surface, (x, y))
        key = path.as_posix()
        mapping[key] = {
            "x": x,
            "y": y,
            "w": surface.get_width(),
            "h": surface.get_height(),
        }

    pygame.image.save(atlas, str(ATLAS_IMAGE))
    ATLAS_JSON.write_text(json.dumps(mapping, indent=2, sort_keys=True), encoding="utf-8")
    log.info("Packed %s wall sprites into %s and %s", len(loaded), ATLAS_IMAGE, ATLAS_JSON)


if __name__ == "__main__":
    pack_walls()
