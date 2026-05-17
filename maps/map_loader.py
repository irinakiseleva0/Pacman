from __future__ import annotations

from pathlib import Path

from maps.generator import BSPMazeGenerator


def load_map_lines(path: str | Path) -> list[str]:
    return Path(path).read_text(encoding="utf-8").splitlines()


def write_map_lines(path: str | Path, lines: list[str]) -> None:
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_bsp_map_lines(width: int = 28, height: int = 30, *, seed: int | None = None) -> list[str]:
    return BSPMazeGenerator(width, height, seed=seed).generate_map_lines()


def write_generated_bsp_map(path: str | Path, width: int = 28, height: int = 30, *, seed: int | None = None) -> None:
    write_map_lines(path, generate_bsp_map_lines(width, height, seed=seed))
