from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

@dataclass
class SaveScoring:
    file_path: Path = Path(__file__).resolve().parent / "scores.txt"
    max_entries: int = 10

    def load_scores(self) -> List[Tuple[str, int]]:
        scores: List[Tuple[str, int]] = []
        if not self.file_path.exists():
            return scores

        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ": " not in line:
                    continue
                name, score_str = line.split(": ", 1)
                try:
                    scores.append((name, int(score_str)))
                except ValueError:
                    continue

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def add_score(self, player_name: str, player_score: int) -> List[Tuple[str, int]]:
        player_name = (player_name or "").replace(":", "").strip() or "Player"
        player_score = int(player_score)

        scores = self.load_scores()
        scores.append((player_name, player_score))
        scores.sort(key=lambda x: x[1], reverse=True)
        scores = scores[: self.max_entries]

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as f:
            for name, score in scores:
                f.write(f"{name}: {score}\n")

        return scores