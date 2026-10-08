import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from battle.models import BattleRoom
from quiz.models import Category, Question, Choice


class BattleTests(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()

        self.user1 = User.objects.create_user(username="player1", password="pass")
        self.user2 = User.objects.create_user(username="player2", password="pass")

        self.category = Category.objects.create(name="Django ORM", slug="django-orm")
        self.questions = []
        for i in range(5):
            q = Question.objects.create(category=self.category, text=f"Savol {i+1}", difficulty="medium")
            Choice.objects.create(question=q, text=f"To'g'ri {i+1}", is_correct=True)
            Choice.objects.create(question=q, text=f"Noto'g'ri {i+1}", is_correct=False)
            self.questions.append(q)

    def test_battle_flow(self):
        self.client1.login(username="player1", password="pass")
        res = self.client1.post(reverse("battle:create"), data={"category_slug": self.category.slug})
        self.assertEqual(res.status_code, 302)

        room = BattleRoom.objects.filter(creator=self.user1).first()
        self.assertIsNotNone(room)
        self.assertEqual(room.status, "waiting")

        self.client2.login(username="player2", password="pass")
        res = self.client2.get(reverse("battle:room", kwargs={"room_code": room.room_code}))
        self.assertEqual(res.status_code, 200)

        room.refresh_from_db()
        self.assertEqual(room.status, "active")
        self.assertEqual(room.opponent, self.user2)

        res = self.client1.get(reverse("battle:api_state", kwargs={"room_code": room.room_code}))
        data = res.json()
        self.assertEqual(data["status"], "active")
        self.assertIsNotNone(data["current_question"])

        q1 = room.questions.order_by("id")[0]
        correct_ch = q1.choices.filter(is_correct=True).first()
        res = self.client1.post(
            reverse("battle:api_answer", kwargs={"room_code": room.room_code}),
            data=json.dumps({"question_id": q1.id, "choice_id": correct_ch.id}),
            content_type="application/json"
        )
        self.assertTrue(res.json()["is_correct"])

        room.refresh_from_db()
        self.assertEqual(room.creator_score, q1.points)
        self.assertEqual(room.creator_progress, 1)
