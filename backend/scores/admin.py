from __future__ import annotations

from django.contrib import admin

from scores.models import Player, Score


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["username", "created_at"]
    search_fields = ["username"]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ["player", "mode", "value", "seed", "date"]
    list_filter = ["mode", "date"]
    search_fields = ["player__username"]
