from django.contrib import admin
from .models import UserScore, Badge, UserBadge


@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "score", "total_questions", "correct_answers", "percentage", "completed_at")
    list_filter = ("category", "completed_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("completed_at",)
    ordering = ("-score", "-completed_at")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "points_reward", "category")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "earned_at")
    list_filter = ("badge", "earned_at")
    search_fields = ("user__username", "badge__name")
