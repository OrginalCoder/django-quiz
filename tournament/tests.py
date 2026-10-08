import json
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from quiz.models import Category, Question, Choice
from .models import Tournament, TournamentParticipation

User = get_user_model()


class TournamentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="turnirchi", password="password123")
        self.category = Category.objects.create(name="Django ORM", slug="django-orm")
        self.question = Question.objects.create(
            category=self.category,
            text="Turnir savoli 1?",
            difficulty="medium",
            code_snippet="User.objects.all()",
            question_type="code_fill"
        )
        self.choice_correct = Choice.objects.create(question=self.question, text="To'g'ri", is_correct=True)
        self.choice_wrong = Choice.objects.create(question=self.question, text="Noto'g'ri", is_correct=False)

        now = timezone.now()
        self.tournament = Tournament.objects.create(
            title="Haftalik Test Turniri",
            slug="haftalik-test-turniri",
            description="Sinov uchun turnir",
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(days=2),
            duration_minutes=15,
            is_active=True
        )
        self.tournament.questions.add(self.question)

    def test_tournament_list_view(self):
        self.client.login(username="turnirchi", password="password123")
        response = self.client.get(reverse("tournament:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Haftalik Test Turniri")

    def test_tournament_play_view(self):
        self.client.login(username="turnirchi", password="password123")
        response = self.client.get(reverse("tournament:play", kwargs={"pk": self.tournament.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Turnir rejimi")

    def test_tournament_submit_api(self):
        self.client.login(username="turnirchi", password="password123")
        self.client.get(reverse("tournament:play", kwargs={"pk": self.tournament.pk}))

        payload = {
            "answers": {str(self.question.id): self.choice_correct.id},
            "time_spent_seconds": 45
        }
        response = self.client.post(
            reverse("tournament:submit", kwargs={"pk": self.tournament.pk}),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))

        participation = TournamentParticipation.objects.get(tournament=self.tournament, user=self.user)
        self.assertIsNotNone(participation.completed_at)
        self.assertEqual(participation.correct_answers, 1)

    def test_tournament_leaderboard_view(self):
        response = self.client.get(reverse("tournament:leaderboard", kwargs={"pk": self.tournament.pk}))
        self.assertEqual(response.status_code, 200)
