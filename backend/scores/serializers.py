from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers

from scores.models import Player, Score


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "username", "created_at"]
        read_only_fields = ["id", "created_at"]


class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Score
        fields = ["id", "player", "username", "mode", "value", "seed", "date"]
        read_only_fields = ["id", "player", "date"]

    def validate_mode(self, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise serializers.ValidationError("Mode is required.")
        return normalized

    def create(self, validated_data: dict) -> Score:
        request = self.context.get("request")
        username = validated_data.pop("username", "")
        if request is not None and request.user.is_authenticated:
            username = request.user.username
        if not username:
            raise serializers.ValidationError({"username": "Provide username or authenticate with JWT."})

        player, _created = Player.objects.get_or_create(username=username)
        return Score.objects.create(player=player, **validated_data)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_username(self, value: str) -> str:
        username = value.strip()
        if not username:
            raise serializers.ValidationError("Username is required.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username is already taken.")
        return username

    def create(self, validated_data: dict) -> User:
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        Player.objects.get_or_create(username=user.username)
        return user
