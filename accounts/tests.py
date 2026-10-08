from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123"
        )

    def test_login_page_renders_with_google_button(self):
        res = self.client.get(reverse("accounts:login"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Google orqali kirish")

    def test_register_page_renders_with_google_button(self):
        res = self.client.get(reverse("accounts:register"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Google orqali davom etish")

    def test_standard_login_flow(self):
        res = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "testpassword123"
        })
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("accounts:dashboard"))

    def test_dashboard_authenticated(self):
        self.client.login(username="testuser", password="testpassword123")
        res = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Salom, testuser!")
