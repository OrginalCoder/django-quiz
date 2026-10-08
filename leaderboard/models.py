from django.db import models
from django.conf import settings


class UserScore(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_scores",
        verbose_name="Foydalanuvchi"
    )
    category = models.ForeignKey(
        "quiz.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="scores",
        verbose_name="Kategoriya"
    )
    score = models.PositiveIntegerField(verbose_name="To'plangan ball")
    total_questions = models.PositiveIntegerField(verbose_name="Jami savollar")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="To'g'ri javoblar soni")
    details = models.JSONField(default=list, blank=True, verbose_name="Batafsil javoblar")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Tugatilgan vaqt")

    class Meta:
        verbose_name = "Foydalanuvchi natijasi"
        verbose_name_plural = "Foydalanuvchi natijalari"
        ordering = ["-score", "-completed_at"]

    def __str__(self):
        cat_name = self.category.name if self.category else "Umumiy"
        return f"{self.user.username} - {cat_name}: {self.score} ball ({self.completed_at:%Y-%m-%d %H:%M})"

    @property
    def percentage(self):
        if self.total_questions > 0:
            return round((self.correct_answers / self.total_questions) * 100)
        return 0


class Badge(models.Model):
    slug = models.SlugField(unique=True, verbose_name="Slug")
    name = models.CharField(max_length=100, verbose_name="Nishon nomi")
    description = models.TextField(verbose_name="Tavsif")
    icon_svg = models.TextField(verbose_name="SVG belgisi")
    points_reward = models.PositiveIntegerField(default=50, verbose_name="Bonus ball")
    category = models.CharField(max_length=30, default="general", verbose_name="Kategoriya")

    class Meta:
        verbose_name = "Nishon"
        verbose_name_plural = "Nishonlar"
        ordering = ["id"]

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="badges",
        verbose_name="Foydalanuvchi"
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="awarded_users",
        verbose_name="Nishon"
    )
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Berilgan vaqt")

    class Meta:
        verbose_name = "Foydalanuvchi nishoni"
        verbose_name_plural = "Foydalanuvchi nishonlari"
        unique_together = ("user", "badge")
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


def award_badges(user):
    if not user or not user.is_authenticated:
        return []
    awarded = []
    scores = UserScore.objects.filter(user=user)
    total_score = sum(s.score for s in scores)
    completed_count = scores.count()
    has_perfect = any(s.percentage == 100 for s in scores)
    battles_won = getattr(user, "won_battles", None)
    battles_won_count = battles_won.count() if battles_won is not None else 0
    resolved_mistakes = getattr(user, "mistakes", None)
    resolved_count = resolved_mistakes.filter(is_resolved=True).count() if resolved_mistakes is not None else 0
    daily_attempts = getattr(user, "daily_attempts", None)
    daily_count = daily_attempts.filter(is_correct=True).count() if daily_attempts is not None else 0

    rules = [
        ("birinchi_qadam", completed_count >= 1),
        ("tajribali", total_score >= 100),
        ("django_ninja", total_score >= 300),
        ("snayper", has_perfect),
        ("duelchi", battles_won_count >= 1),
        ("xatolar_ustasi", resolved_count >= 1),
        ("kunlik_qahramon", daily_count >= 1),
    ]

    for slug, condition in rules:
        if condition:
            badge = Badge.objects.filter(slug=slug).first()
            if badge and not UserBadge.objects.filter(user=user, badge=badge).exists():
                ub = UserBadge.objects.create(user=user, badge=badge)
                awarded.append(ub)
    return awarded
