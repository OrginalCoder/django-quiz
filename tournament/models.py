from django.db import models
from django.conf import settings
from django.utils import timezone


class Tournament(models.Model):
    title = models.CharField(max_length=150, verbose_name="Turnir nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Turnir haqida")
    start_date = models.DateTimeField(verbose_name="Boshlanish vaqti")
    end_date = models.DateTimeField(verbose_name="Tugash vaqti")
    duration_minutes = models.PositiveIntegerField(default=15, verbose_name="Ajratilgan vaqt (daqiqa)")
    questions = models.ManyToManyField("quiz.Question", related_name="tournaments", verbose_name="Turnir savollari")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    prize_title = models.CharField(max_length=120, default="Haftalik Django Chempioni Kubogi", verbose_name="Mukofot")

    class Meta:
        verbose_name = "Turnir"
        verbose_name_plural = "Turnirlar"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    @property
    def is_currently_running(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def is_upcoming(self):
        return timezone.now() < self.start_date

    @property
    def is_ended(self):
        return timezone.now() > self.end_date or not self.is_active

    @property
    def participants_count(self):
        return self.participations.count()


class TournamentParticipation(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="participations",
        verbose_name="Turnir"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tournament_attempts",
        verbose_name="Foydalanuvchi"
    )
    score = models.PositiveIntegerField(default=0, verbose_name="To'plangan ball")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="To'g'ri javoblar")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Jami savollar")
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name="Sarflangan vaqt (soniya)")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Boshlangan vaqt")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugallangan vaqt")

    class Meta:
        verbose_name = "Turnir ishtirokchisi"
        verbose_name_plural = "Turnir ishtirokchilari"
        unique_together = ("tournament", "user")
        ordering = ["-score", "time_spent_seconds"]

    def __str__(self):
        return f"{self.user.username} - {self.tournament.title}: {self.score} ball"

    @property
    def percentage(self):
        if self.total_questions > 0:
            return round((self.correct_answers / self.total_questions) * 100)
        return 0
