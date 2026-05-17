from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from scores.models import Player, Score
from scores.serializers import PlayerSerializer, RegisterSerializer, ScoreSerializer


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.AllowAny]


class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self) -> QuerySet[Score]:
        queryset = Score.objects.select_related("player")
        mode = self.request.query_params.get("mode")
        if mode:
            queryset = queryset.filter(mode=mode.strip().lower())
        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(player__username=username.strip())
        return queryset.order_by("-date")


class LeaderboardView(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self) -> QuerySet[Score]:
        queryset = Score.objects.select_related("player")
        mode = self.request.query_params.get("mode")
        if mode:
            queryset = queryset.filter(mode=mode.strip().lower())
        return queryset.order_by("-value", "date")[:100]


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )
