from __future__ import annotations


ABILITY_UNLOCK_RANKS: dict[str, int] = {
    "Dash": 5,
    "Shield": 10,
    "Slow": 15,
}


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
