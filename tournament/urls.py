from django.urls import path
from .views import (
    TournamentListView,
    TournamentDetailView,
    TournamentPlayView,
    TournamentSubmitApiView,
    TournamentLeaderboardView,
)

app_name = "tournament"

urlpatterns = [
    path("tournaments/", TournamentListView.as_view(), name="list"),
    path("tournaments/<int:pk>/", TournamentDetailView.as_view(), name="detail"),
    path("tournaments/<int:pk>/play/", TournamentPlayView.as_view(), name="play"),
    path("tournaments/<int:pk>/submit/", TournamentSubmitApiView.as_view(), name="submit"),
    path("tournaments/<int:pk>/leaderboard/", TournamentLeaderboardView.as_view(), name="leaderboard"),
]
