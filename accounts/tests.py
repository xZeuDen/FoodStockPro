from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class AccountsTests(TestCase):
    def test_creating_user_automatically_creates_profile(self):
        user = User.objects.create_user(username="testuser", password="password")

        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.role, Profile.MANAGER)

    def test_profile_role_can_be_set_to_manager(self):
        user = User.objects.create_user(username="manager1", password="password")
        user.profile.role = Profile.MANAGER
        user.profile.save()

        self.assertEqual(user.profile.role, Profile.MANAGER)

    def test_register_page_loads_successfully(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    def test_login_page_loads_successfully(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
