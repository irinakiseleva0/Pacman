from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from scores.views import LeaderboardView, PlayerViewSet, RegisterView, ScoreViewSet


router = DefaultRouter()
router.register("scores", ScoreViewSet, basename="score")
router.register("profiles", PlayerViewSet, basename="profile")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
