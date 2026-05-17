from __future__ import annotations

from django.db import models


class Player(models.Model):
    username = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return self.username


class Score(models.Model):
    player = models.ForeignKey(Player, related_name="scores", on_delete=models.CASCADE)
    mode = models.CharField(max_length=32, db_index=True)
    value = models.PositiveIntegerField()
    seed = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-value", "date"]
        indexes = [
            models.Index(fields=["mode", "-value"], name="score_mode_value_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.player.username} {self.mode} {self.value}"
