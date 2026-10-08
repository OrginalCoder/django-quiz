from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from leaderboard.models import UserScore
from quiz.models import Category


class LeaderboardOrderingAndFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.user3 = User.objects.create_user(username="user3", password="pass")

        self.cat1 = Category.objects.create(name="Cat 1", slug="cat-1")
        self.cat2 = Category.objects.create(name="Cat 2", slug="cat-2")

        self.score1 = UserScore.objects.create(
            user=self.user1, category=self.cat1, score=15, total_questions=10, correct_answers=7
        )
        self.score2 = UserScore.objects.create(
            user=self.user2, category=self.cat1, score=25, total_questions=10, correct_answers=10
        )
        self.score3 = UserScore.objects.create(
            user=self.user3, category=self.cat2, score=20, total_questions=10, correct_answers=9
        )

    def test_leaderboard_overall_ordering(self):
        res = self.client.get(reverse("leaderboard:leaderboard"))
        self.assertEqual(res.status_code, 200)

        scores_in_context = list(res.context["scores"])
        self.assertEqual(scores_in_context[0], self.score2)
        self.assertEqual(scores_in_context[1], self.score3)
        self.assertEqual(scores_in_context[2], self.score1)

        self.assertEqual(res.context["top_1"], self.score2)
        self.assertEqual(res.context["top_2"], self.score3)
        self.assertEqual(res.context["top_3"], self.score1)

    def test_leaderboard_category_filter(self):
        res = self.client.get(reverse("leaderboard:leaderboard") + "?category=cat-1")
        self.assertEqual(res.status_code, 200)

        scores_in_context = list(res.context["scores"])
        self.assertEqual(len(scores_in_context), 2)
        self.assertEqual(scores_in_context[0], self.score2)
        self.assertEqual(scores_in_context[1], self.score1)

    def test_certificate_download_eligible(self):
        self.client.login(username="user2", password="pass")
        res = self.client.get(reverse("leaderboard:download_certificate", kwargs={"score_id": self.score2.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/pdf")

    def test_award_badges_system(self):
        from leaderboard.models import Badge, UserBadge, award_badges
        Badge.objects.create(slug="birinchi_qadam", name="Birinchi qadam", description="Ilk test", icon_svg="<svg></svg>")
        Badge.objects.create(slug="snayper", name="Snayper", description="100%", icon_svg="<svg></svg>")
        awarded = award_badges(self.user2)
        self.assertTrue(len(awarded) >= 1)
        self.assertTrue(UserBadge.objects.filter(user=self.user2, badge__slug="snayper").exists())
