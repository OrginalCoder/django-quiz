import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from quiz.models import Category, Question, Choice
from leaderboard.models import UserScore


class QuizScoringAndModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Django Asoslari",
            slug="django-asoslari",
            icon="layers",
            description="Django asosiy tushunchalari"
        )
        self.q_easy = Question.objects.create(
            category=self.category,
            text="Django nima?",
            difficulty="easy"
        )
        self.q_medium = Question.objects.create(
            category=self.category,
            text="ORM nima?",
            difficulty="medium"
        )
        self.q_hard = Question.objects.create(
            category=self.category,
            text="select_related qanday ishlaydi?",
            difficulty="hard"
        )

    def test_difficulty_weights(self):
        self.assertEqual(self.q_easy.points, 1)
        self.assertEqual(self.q_medium.points, 2)
        self.assertEqual(self.q_hard.points, 3)

    def test_category_question_count(self):
        self.assertEqual(self.category.question_count, 3)


class GuestAccessRestrictionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.category = Category.objects.create(
            name="Django ORM",
            slug="django-orm",
            icon="database"
        )
        self.question = Question.objects.create(
            category=self.category,
            text="Filter nima?",
            difficulty="easy"
        )
        self.choice = Choice.objects.create(
            question=self.question,
            text="To'g'ri variant",
            is_correct=True
        )

    def test_public_pages_accessible_to_guest(self):
        res = self.client.get(reverse("core:landing"))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse("quiz:category_detail", kwargs={"slug": self.category.slug}))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse("leaderboard:leaderboard"))
        self.assertEqual(res.status_code, 200)

    def test_guest_quiz_attempt_redirects_with_message(self):
        quiz_url = reverse("quiz:quiz_screen", kwargs={"category_slug": self.category.slug})
        res = self.client.get(quiz_url, follow=True)
        login_url = reverse("accounts:login")
        self.assertRedirects(res, f"{login_url}?next={quiz_url}")

        messages = list(res.context["messages"])
        self.assertTrue(any("Viktorinada qatnashish uchun tizimga kiring" in m.message for m in messages))

    def test_guest_dashboard_redirects_to_login(self):
        res = self.client.get(reverse("accounts:dashboard"))
        login_url = reverse("accounts:login")
        self.assertRedirects(res, f"{login_url}?next={reverse('accounts:dashboard')}")


class QuizFlowAndDecoupledSignalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student1", password="password123")
        self.client.login(username="student1", password="password123")

        self.category = Category.objects.create(
            name="Django Views",
            slug="django-views",
            icon="shield"
        )
        self.q1 = Question.objects.create(
            category=self.category,
            text="CBV nima?",
            difficulty="easy"
        )
        self.q1_c1 = Choice.objects.create(question=self.q1, text="Klassga asoslangan ko'rinish", is_correct=True)
        self.q1_c2 = Choice.objects.create(question=self.q1, text="Funksiya", is_correct=False)

        self.q2 = Question.objects.create(
            category=self.category,
            text="LoginRequiredMixin nima?",
            difficulty="hard"
        )
        self.q2_c1 = Choice.objects.create(question=self.q2, text="Autentifikatsiya mixini", is_correct=True)
        self.q2_c2 = Choice.objects.create(question=self.q2, text="Xatolik klassi", is_correct=False)

    def test_quiz_session_flow_and_score_creation(self):
        res = self.client.get(reverse("quiz:quiz_screen", kwargs={"category_slug": self.category.slug}))
        self.assertEqual(res.status_code, 200)

        session = self.client.session
        qs = session["quiz_session"]
        qs["question_ids"] = [self.q1.id, self.q2.id]
        session["quiz_session"] = qs
        session.save()

        res = self.client.get(reverse("quiz:api_question", kwargs={"category_slug": self.category.slug}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["question_id"], self.q1.id)
        self.assertEqual(data["current_index"], 1)
        self.assertEqual(data["total_questions"], 2)

        res = self.client.post(
            reverse("quiz:api_answer", kwargs={"category_slug": self.category.slug}),
            data=json.dumps({"question_id": self.q1.id, "choice_id": self.q1_c1.id}),
            content_type="application/json"
        )
        data = res.json()
        self.assertTrue(data["is_correct"])
        self.assertEqual(data["points_earned"], 1)
        self.assertFalse(data["is_finished"])

        res = self.client.get(reverse("quiz:api_question", kwargs={"category_slug": self.category.slug}))
        data = res.json()
        self.assertEqual(data["question_id"], self.q2.id)
        self.assertEqual(data["current_index"], 2)

        res = self.client.post(
            reverse("quiz:api_answer", kwargs={"category_slug": self.category.slug}),
            data=json.dumps({"question_id": self.q2.id, "choice_id": self.q2_c1.id}),
            content_type="application/json"
        )
        data = res.json()
        self.assertTrue(data["is_correct"])
        self.assertEqual(data["points_earned"], 3)
        self.assertTrue(data["is_finished"])
        self.assertIsNotNone(data["next_url"])

        score_record = UserScore.objects.filter(user=self.user, category=self.category).first()
        self.assertIsNotNone(score_record)
        self.assertEqual(score_record.score, 4)
        self.assertEqual(score_record.total_questions, 2)
        self.assertEqual(score_record.correct_answers, 2)
        self.assertEqual(score_record.percentage, 100)

        result_url = reverse("leaderboard:result", kwargs={"score_id": score_record.id})
        res = self.client.get(result_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "4")


class ResultOwnerOnlyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner_user", password="password123")
        self.intruder = User.objects.create_user(username="intruder_user", password="password123")
        self.score = UserScore.objects.create(
            user=self.owner,
            score=15,
            total_questions=10,
            correct_answers=8
        )

    def test_intruder_cannot_view_others_result(self):
        self.client.login(username="intruder_user", password="password123")
        res = self.client.get(reverse("leaderboard:result", kwargs={"score_id": self.score.id}))
        self.assertEqual(res.status_code, 403)


class MistakesAndDailyChallengeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_student", password="password123")
        self.category = Category.objects.create(name="Modellar", slug="modellar")
        self.q = Question.objects.create(category=self.category, text="Django nima?", difficulty="easy")
        self.c_corr = Choice.objects.create(question=self.q, text="Framework", is_correct=True)
        self.c_wrong = Choice.objects.create(question=self.q, text="Til", is_correct=False)

    def test_mistake_recording_and_list_view(self):
        self.client.login(username="test_student", password="password123")
        self.client.get(reverse("quiz:quiz_screen", kwargs={"category_slug": self.category.slug}))

        res = self.client.post(
            reverse("quiz:api_answer", kwargs={"category_slug": self.category.slug}),
            data=json.dumps({"question_id": self.q.id, "choice_id": self.c_wrong.id}),
            content_type="application/json"
        )
        self.assertFalse(res.json()["is_correct"])

        res = self.client.get(reverse("quiz:mistakes_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["unresolved_count"], 1)

    def test_daily_challenge_view_and_answer(self):
        self.client.login(username="test_student", password="password123")
        res = self.client.get(reverse("quiz:daily_challenge"))
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            reverse("quiz:daily_answer"),
            data=json.dumps({"choice_id": self.c_corr.id}),
            content_type="application/json"
        )
        data = res.json()
        self.assertTrue(data["is_correct"])
        self.assertEqual(data["bonus_points"], 5)

    def test_ai_explain_api(self):
        self.client.login(username="test_student", password="password123")
        res = self.client.get(reverse("quiz:ai_explain", kwargs={"question_id": self.q.id}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("explanation", data)
        self.assertEqual(data["correct_choice"], self.c_corr.text)

