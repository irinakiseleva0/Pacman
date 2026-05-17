from __future__ import annotations

from concurrent.futures import Future

from utils.api_client import LeaderboardClient


class HighScoreService:
    def __init__(self, client: LeaderboardClient | None = None) -> None:
        self.client = client or LeaderboardClient()
        self.leaderboard_future: Future | None = None
        self.submit_future: Future | None = None

    def refresh_leaderboard(self, mode: str, limit: int = 10) -> None:
        self.leaderboard_future = self.client.fetch_leaderboard_async(mode, limit)

    def submit_score(self, mode: str, value: int, seed: int) -> None:
        self.submit_future = self.client.submit_score_async(mode, value, seed)

    def leaderboard_ready(self) -> bool:
        return self.leaderboard_future is not None and self.leaderboard_future.done()

    def leaderboard(self) -> list[dict]:
        if not self.leaderboard_ready():
            return []
        return self.leaderboard_future.result()

    def close(self) -> None:
        self.client.close()
