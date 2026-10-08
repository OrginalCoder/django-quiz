from django.contrib import admin
from .models import BattleRoom


@admin.register(BattleRoom)
class BattleRoomAdmin(admin.ModelAdmin):
    list_display = ("room_code", "category", "creator", "opponent", "status", "winner", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("room_code", "creator__username", "opponent__username")
