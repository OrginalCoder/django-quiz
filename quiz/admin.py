from django.contrib import admin
from .models import Category, Question, Choice, UserMistake, DailyChallenge, DailyChallengeAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    min_num = 2


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "question_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "category", "difficulty", "points", "choices_count")
    list_filter = ("category", "difficulty")
    search_fields = ("text",)
    inlines = [ChoiceInline]

    def text_preview(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text
    text_preview.short_description = "Savol"

    def choices_count(self, obj):
        return obj.choices.count()
    choices_count.short_description = "Variantlar soni"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct", "question__category")
    search_fields = ("text", "question__text")


@admin.register(UserMistake)
class UserMistakeAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "is_resolved", "created_at")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("user__username", "question__text")


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ("date", "question", "bonus_points")
    list_filter = ("date",)
    search_fields = ("question__text",)


@admin.register(DailyChallengeAttempt)
class DailyChallengeAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "challenge", "is_correct", "attempted_at")
    list_filter = ("is_correct", "attempted_at")
    search_fields = ("user__username",)
