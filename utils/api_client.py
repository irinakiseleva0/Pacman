from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import os

import requests

from utils.score_storage import load_high_score, save_high_score


class LeaderboardClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        token: str | None = None,
        username: str = "local-player",
        timeout: float = 3.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("PACMAN_API_URL") or "http://127.0.0.1:8000").rstrip("/")
        self.token = token or os.environ.get("PACMAN_API_TOKEN")
        self.username = username
        self.timeout = timeout
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="leaderboard-api")

    def submit_score(self, mode: str, value: int, seed: int) -> dict:
        payload = {
            "mode": self._normalize_mode(mode),
            "value": int(value),
            "seed": int(seed),
        }
        if not self.token:
            payload["username"] = self.username

        try:
            response = requests.post(
                f"{self.base_url}/api/scores/",
                json=payload,
                headers=self._auth_headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else {"result": data}
        except requests.RequestException as exc:
            self._save_local_score(value)
            return {
                "offline": True,
                "error": str(exc),
                "mode": payload["mode"],
                "value": int(value),
                "seed": int(seed),
            }

    def fetch_leaderboard(self, mode: str, limit: int = 10) -> list[dict]:
        normalized_mode = self._normalize_mode(mode)
        try:
            response = requests.get(
                f"{self.base_url}/api/leaderboard/",
                params={"mode": normalized_mode},
                headers=self._auth_headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                return self._local_leaderboard(normalized_mode, limit)
            return [entry for entry in data[: max(0, int(limit))] if isinstance(entry, dict)]
        except requests.RequestException:
            return self._local_leaderboard(normalized_mode, limit)

    def submit_score_async(self, mode: str, value: int, seed: int) -> Future:
        return self._executor.submit(self.submit_score, mode, value, seed)

    def fetch_leaderboard_async(self, mode: str, limit: int = 10) -> Future:
        return self._executor.submit(self.fetch_leaderboard, mode, limit)

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def _normalize_mode(self, mode: str) -> str:
        return str(mode).strip().lower().replace(" ", "_")

    def _save_local_score(self, value: int) -> None:
        current = load_high_score()
        if int(value) > current:
            save_high_score(int(value))

    def _local_leaderboard(self, mode: str, limit: int) -> list[dict]:
        high_score = load_high_score()
        if high_score <= 0 or limit <= 0:
            return []
        return [
            {
                "offline": True,
                "player": {"username": self.username},
                "mode": mode,
                "value": high_score,
                "seed": 0,
                "date": None,
            }
        ]
