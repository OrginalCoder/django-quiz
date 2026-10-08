from django.contrib import admin
from .models import Tournament, TournamentParticipation


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "is_active", "duration_minutes")
    list_filter = ("is_active", "start_date")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("questions",)


@admin.register(TournamentParticipation)
class TournamentParticipationAdmin(admin.ModelAdmin):
    list_display = ("tournament", "user", "score", "correct_answers", "time_spent_seconds", "completed_at")
    list_filter = ("tournament", "completed_at")
    search_fields = ("user__username", "tournament__title")
