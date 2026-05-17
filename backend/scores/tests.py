from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from scores.models import Player, Score


class ScoresApiTests(APITestCase):
    def test_register_creates_user_and_player_profile(self) -> None:
        response = self.client.post(
            reverse("register"),
            {"username": "iris", "password": "strong-pass-123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Player.objects.filter(username="iris").exists())

    def test_score_post_creates_score_with_username(self) -> None:
        response = self.client.post(
            "/api/scores/",
            {"username": "iris", "mode": "Arcade", "value": 9000, "seed": 123456},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Score.objects.get().mode, "arcade")
        self.assertEqual(Score.objects.get().player.username, "iris")

    def test_leaderboard_filters_by_mode_and_orders_by_value(self) -> None:
        player = Player.objects.create(username="iris")
        Score.objects.create(player=player, mode="arcade", value=100, seed=1)
        Score.objects.create(player=player, mode="arcade", value=300, seed=2)
        Score.objects.create(player=player, mode="dailychallenge", value=999, seed=3)

        response = self.client.get("/api/leaderboard/?mode=arcade")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["value"] for item in response.data], [300, 100])
