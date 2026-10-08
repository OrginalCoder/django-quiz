from django.urls import path
from .views import LeaderboardView, ResultView, CertificateDownloadView

app_name = "leaderboard"

urlpatterns = [
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("result/<int:score_id>/", ResultView.as_view(), name="result"),
    path("certificate/<int:score_id>/", CertificateDownloadView.as_view(), name="download_certificate"),
]
