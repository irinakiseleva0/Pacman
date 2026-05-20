from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

import core.raylib_api as pyray

REPLAY_DIR = Path(__file__).resolve().parents[1] / "data" / "replays"
REPLAY_VERSION = 1


def ensure_replay_dir() -> Path:
    REPLAY_DIR.mkdir(parents=True, exist_ok=True)
    return REPLAY_DIR


def _input_snapshot() -> dict[str, bool]:
    return {
        "up": bool(pyray.is_key_down(pyray.KEY_UP) or pyray.is_key_down(pyray.KEY_W)),
        "down": bool(pyray.is_key_down(pyray.KEY_DOWN) or pyray.is_key_down(pyray.KEY_S)),
        "left": bool(pyray.is_key_down(pyray.KEY_LEFT) or pyray.is_key_down(pyray.KEY_A)),
        "right": bool(pyray.is_key_down(pyray.KEY_RIGHT) or pyray.is_key_down(pyray.KEY_D)),
        "space": bool(pyray.is_key_down(pyray.KEY_SPACE)),
    }


def _actor_pos(actor) -> dict[str, Any]:
    return {
        "kind": str(getattr(actor, "kind", type(actor).__name__)),
        "name": type(actor).__name__,
        "x": int(getattr(actor, "x", 0)),
        "y": int(getattr(actor, "y", 0)),
        "state": str(getattr(actor, "state", "")),
    }


@dataclass(frozen=True)
class ReplayInfo:
    path: Path
    score: int
    seed: int
    date: str
    frames: int


class ReplayRecorder:
    def __init__(self) -> None:
        self.frames: list[dict[str, Any]] = []
        self.last_state: dict[str, Any] | None = None
        self.frame = 0
        self.active = False
        self.metadata: dict[str, Any] = {}
        self.saved_path: Path | None = None

    def start(self, *, seed: int, mode: str, map_name: str) -> None:
        self.frames = []
        self.last_state = None
        self.frame = 0
        self.active = True
        self.saved_path = None
        self.metadata = {
            "version": REPLAY_VERSION,
            "seed": int(seed),
            "mode": str(mode),
            "map": str(map_name),
            "started_at": datetime.now().isoformat(timespec="seconds"),
        }

    def stop(self) -> None:
        self.active = False

    def record_tick(self, ctx) -> None:
        if not self.active:
            return
        game_map = getattr(ctx.runtime, "game_map", None)
        pacman = getattr(ctx.runtime, "pacman", None)
        if game_map is None or pacman is None:
            return
        ghosts = [
            _actor_pos(actor)
            for actor in getattr(game_map, "dynamic_actors", [])
            if getattr(actor, "kind", None) == "ghost"
        ]
        state = {
            "input": _input_snapshot(),
            "pacman_pos": _actor_pos(pacman),
            "ghost_positions": ghosts,
            "score": int(getattr(ctx, "score", 0)),
            "level": int(getattr(ctx, "current_level", 1)),
        }
        delta = {
            key: value
            for key, value in state.items()
            if self.last_state is None or self.last_state.get(key) != value
        }
        if delta:
            delta["frame"] = self.frame
            self.frames.append(delta)
            self.last_state = state
        self.frame += 1

    def save(self, *, score: int, seed: int | None = None) -> Path:
        ensure_replay_dir()
        replay_seed = int(seed if seed is not None else self.metadata.get("seed", 0))
        date_label = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{int(score)}_{replay_seed}_{date_label}.replay"
        path = REPLAY_DIR / filename
        payload = {
            "metadata": {
                **self.metadata,
                "score": int(score),
                "seed": replay_seed,
                "frames_recorded": self.frame,
                "saved_at": datetime.now().isoformat(timespec="seconds"),
            },
            "frames": self.frames,
        }
        path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        self.saved_path = path
        return path


class ReplayPlayer:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.metadata = dict(self.payload.get("metadata", {}))
        self.deltas = list(self.payload.get("frames", []))
        self.index = 0
        self.frame = 0
        self.state: dict[str, Any] = {}

    @property
    def total_frames(self) -> int:
        return int(self.metadata.get("frames_recorded", 0))

    def reset(self) -> None:
        self.index = 0
        self.frame = 0
        self.state = {}

    def seek_next(self) -> dict[str, Any]:
        while self.index < len(self.deltas) and int(self.deltas[self.index].get("frame", 0)) <= self.frame:
            delta = dict(self.deltas[self.index])
            delta.pop("frame", None)
            self.state.update(delta)
            self.index += 1
        self.frame += 1
        return self.state

    def apply_to_map(self, game_map) -> None:
        pacman_state = self.state.get("pacman_pos")
        if pacman_state is not None:
            pacman = getattr(getattr(game_map, "ctx", None), "runtime", None)
            pacman = getattr(pacman, "pacman", None)
            if pacman is not None:
                pacman.x = int(pacman_state.get("x", pacman.x))
                pacman.y = int(pacman_state.get("y", pacman.y))
        ghost_states = self.state.get("ghost_positions", [])
        ghosts = [actor for actor in getattr(game_map, "dynamic_actors", []) if getattr(actor, "kind", None) == "ghost"]
        for actor, ghost_state in zip(ghosts, ghost_states):
            actor.x = int(ghost_state.get("x", actor.x))
            actor.y = int(ghost_state.get("y", actor.y))

    def current_input(self) -> dict[str, bool]:
        return dict(self.state.get("input", {}))

    def apply_to_context(self, ctx) -> None:
        ctx.runtime.replay_input = self.current_input()
        game_map = getattr(ctx.runtime, "game_map", None)
        if game_map is not None:
            self.apply_to_map(game_map)


def list_replays(limit: int = 5) -> list[ReplayInfo]:
    ensure_replay_dir()
    infos: list[ReplayInfo] = []
    for path in REPLAY_DIR.glob("*.replay"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            meta = payload.get("metadata", {})
            infos.append(
                ReplayInfo(
                    path=path,
                    score=int(meta.get("score", 0)),
                    seed=int(meta.get("seed", 0)),
                    date=str(meta.get("saved_at", meta.get("started_at", ""))),
                    frames=int(meta.get("frames_recorded", 0)),
                )
            )
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return sorted(infos, key=lambda item: (item.score, item.date), reverse=True)[:limit]
