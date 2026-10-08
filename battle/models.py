from django.db import models
from django.conf import settings


class BattleRoom(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Kutilmoqda"),
        ("active", "Davom etmoqda"),
        ("finished", "Yakunlangan"),
    ]

    room_code = models.CharField(max_length=20, unique=True, verbose_name="Xona kodi")
    category = models.ForeignKey(
        "quiz.Category",
        on_delete=models.CASCADE,
        related_name="battles",
        null=True,
        blank=True,
        verbose_name="Kategoriya"
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_battles",
        verbose_name="Tashkilotchi"
    )
    opponent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="joined_battles",
        null=True,
        blank=True,
        verbose_name="Raqib"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="waiting", verbose_name="Holat")
    questions = models.ManyToManyField("quiz.Question", related_name="battles", verbose_name="Savollar")
    creator_score = models.PositiveIntegerField(default=0, verbose_name="Tashkilotchi bali")
    opponent_score = models.PositiveIntegerField(default=0, verbose_name="Raqib bali")
    creator_progress = models.PositiveIntegerField(default=0, verbose_name="Tashkilotchi bosqichi")
    opponent_progress = models.PositiveIntegerField(default=0, verbose_name="Raqib bosqichi")
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_battles",
        verbose_name="G'olib"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")

    class Meta:
        verbose_name = "1v1 Bellashuv xonasi"
        verbose_name_plural = "1v1 Bellashuv xonalari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.room_code} ({self.get_status_display()})"
