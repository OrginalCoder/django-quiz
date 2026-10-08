from django.db import models
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Belgi")
    description = models.TextField(blank=True, verbose_name="Tavsif")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def svg_icon(self):
        icons = {
            "django-models-migrations": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>',
            "django-orm-queries": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
            "django-views-auth": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>',
            "django-forms-validation": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
        }
        svg = icons.get(self.slug, '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>')
        return mark_safe(svg)


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Oson"),
        ("medium", "O'rta"),
        ("hard", "Qiyin"),
    ]
    DIFFICULTY_POINTS = {
        "easy": 1,
        "medium": 2,
        "hard": 3,
    }

    category = models.ForeignKey(
        Category,
        related_name="questions",
        on_delete=models.CASCADE,
        verbose_name="Kategoriya"
    )
    text = models.TextField(verbose_name="Savol matni")
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="medium",
        verbose_name="Qiyinlik darajasi"
    )
    code_snippet = models.TextField(blank=True, default="", verbose_name="Kod parchasi")
    question_type = models.CharField(
        max_length=20,
        choices=[("choice", "Oddiy variantlar"), ("code_fill", "Koddagi bo'sh joyni to'ldirish")],
        default="choice",
        verbose_name="Savol turi"
    )
    explanation = models.TextField(blank=True, default="", verbose_name="Tushuntirish / Izoh")

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"

    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.text[:50]}"

    @property
    def points(self):
        return self.DIFFICULTY_POINTS.get(self.difficulty, 1)


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        related_name="choices",
        on_delete=models.CASCADE,
        verbose_name="Savol"
    )
    text = models.CharField(max_length=255, verbose_name="Variant matni")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javobmi?")

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variantlar"

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text}"


class UserMistake(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mistakes",
        verbose_name="Foydalanuvchi"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_mistakes",
        verbose_name="Savol"
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tanlangan noto'g'ri javob"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Xato qilingan vaqt")
    is_resolved = models.BooleanField(default=False, verbose_name="To'g'rilandimi?")

    class Meta:
        verbose_name = "Xato qilingan savol"
        verbose_name_plural = "Xato qilingan savollar"
        unique_together = ("user", "question")


class DailyChallenge(models.Model):
    date = models.DateField(unique=True, verbose_name="Sana")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="daily_challenges",
        verbose_name="Savol"
    )
    bonus_points = models.PositiveIntegerField(default=5, verbose_name="Bonus ball")

    class Meta:
        verbose_name = "Kunlik savol"
        verbose_name_plural = "Kunlik savollar"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.question.text[:40]}"


class DailyChallengeAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_attempts",
        verbose_name="Foydalanuvchi"
    )
    challenge = models.ForeignKey(
        DailyChallenge,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Kunlik sinov"
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tanlangan javob"
    )
    is_correct = models.BooleanField(default=False, verbose_name="To'g'rimi?")
    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name="Urinilgan vaqt")

    class Meta:
        verbose_name = "Kunlik savol urinishi"
        verbose_name_plural = "Kunlik savol urinishlari"
        unique_together = ("user", "challenge")
