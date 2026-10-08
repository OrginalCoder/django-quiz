from django.urls import path
from .views import (
    BattleLobbyView,
    BattleCreateView,
    BattleRoomView,
    BattleStateApiView,
    BattleAnswerApiView,
)

app_name = "battle"

urlpatterns = [
    path("battle/", BattleLobbyView.as_view(), name="lobby"),
    path("battle/create/", BattleCreateView.as_view(), name="create"),
    path("battle/room/<str:room_code>/", BattleRoomView.as_view(), name="room"),
    path("battle/room/<str:room_code>/state/", BattleStateApiView.as_view(), name="api_state"),
    path("battle/room/<str:room_code>/answer/", BattleAnswerApiView.as_view(), name="api_answer"),
]
