from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


ABILITY_UNLOCK_RANKS: dict[str, int] = {
    "Dash": 5,
    "Shield": 10,
    "Slow": 15,
}

DIALOGUE_PATH = Path(__file__).resolve().parents[1] / "data" / "dialogue.json"


@dataclass(frozen=True)
class DialogueEntry:
    level_trigger: int | str
    character: str
    text: str
    portrait: str


def load_dialogue_entries(path: Path = DIALOGUE_PATH) -> tuple[DialogueEntry, ...]:
    if not path.exists():
        return ()
    raw_entries = json.loads(path.read_text(encoding="utf-8"))
    entries: list[DialogueEntry] = []
    for raw in raw_entries:
        entries.append(
            DialogueEntry(
                level_trigger=raw["level_trigger"],
                character=str(raw["character"]),
                text=str(raw["text"]),
                portrait=str(raw["portrait"]),
            )
        )
    return tuple(entries)


def dialogue_triggers_for_level(level: int) -> tuple[int | str, ...]:
    triggers: list[int | str] = [level]
    if level == 5:
        triggers.append("boss1")
    return tuple(triggers)


def dialogue_for_level(level: int, entries: tuple[DialogueEntry, ...] | None = None) -> tuple[DialogueEntry, ...]:
    available = entries if entries is not None else load_dialogue_entries()
    triggers = dialogue_triggers_for_level(level)
    return tuple(entry for entry in available if entry.level_trigger in triggers)


def serialize_dialogue(entries: tuple[DialogueEntry, ...]) -> list[dict[str, str | int]]:
    return [
        {
            "level_trigger": entry.level_trigger,
            "character": entry.character,
            "text": entry.text,
            "portrait": entry.portrait,
        }
        for entry in entries
    ]


def career_rank_level(ctx) -> int:
    score_fn = getattr(ctx, "career_rank_score", None)
    if callable(score_fn):
        return max(1, int(score_fn() // 1000) + 1)

    profile = getattr(ctx, "profile", {}) or {}
    score = (
        int(profile.get("best_score", 0))
        + int(profile.get("total_levels_cleared", 0)) * 400
        + int(profile.get("total_ghosts_eaten", 0)) * 30
        + int(profile.get("total_wins", 0)) * 1200
    )
    return max(1, score // 1000 + 1)


def unlocked_abilities(ctx) -> dict[str, bool]:
    rank = career_rank_level(ctx)
    return {name: rank >= required_rank for name, required_rank in ABILITY_UNLOCK_RANKS.items()}


def ability_unlock_lines(ctx) -> tuple[str, ...]:
    rank = career_rank_level(ctx)
    return tuple(
        f"{name} at rank {required_rank}"
        for name, required_rank in ABILITY_UNLOCK_RANKS.items()
        if rank < required_rank
    )
