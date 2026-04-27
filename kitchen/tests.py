from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from inventory.models import Ingredient, IngredientCategory

from .models import IngredientRequest


class KitchenTests(TestCase):
    def setUp(self):
        self.kitchen_user = User.objects.create_user(
            username="kitchen1",
            password="password",
        )
        self.kitchen_user.profile.role = Profile.KITCHEN
        self.kitchen_user.profile.save()

        self.manager = User.objects.create_user(
            username="manager1",
            password="password",
        )
        self.manager.profile.role = Profile.MANAGER
        self.manager.profile.save()

        self.category = IngredientCategory.objects.create(name="Dairy")
        self.ingredient = Ingredient.objects.create(
            category=self.category,
            name="Milk",
            unit=Ingredient.LITRES,
            current_stock=Decimal("8.00"),
            minimum_stock=Decimal("12.00"),
            cost_per_unit=Decimal("1.10"),
        )

    def test_kitchen_staff_can_create_ingredient_request(self):
        self.client.login(username="kitchen1", password="password")

        response = self.client.post(
            reverse("kitchen:ingredient_request_create"),
            {
                "ingredient": self.ingredient.id,
                "quantity": "5.00",
                "reason": "Breakfast menu stock running low",
            },
        )

        self.assertEqual(response.status_code, 302)
        ingredient_request = IngredientRequest.objects.get()
        self.assertEqual(ingredient_request.requested_by, self.kitchen_user)
        self.assertEqual(ingredient_request.status, IngredientRequest.PENDING)

    def test_manager_can_view_ingredient_requests(self):
        IngredientRequest.objects.create(
            ingredient=self.ingredient,
            requested_by=self.kitchen_user,
            quantity=Decimal("5.00"),
            reason="Breakfast menu stock running low",
        )
        self.client.login(username="manager1", password="password")

        response = self.client.get(reverse("kitchen:ingredient_request_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Milk")

    def test_manager_can_approve_ingredient_request(self):
        ingredient_request = IngredientRequest.objects.create(
            ingredient=self.ingredient,
            requested_by=self.kitchen_user,
            quantity=Decimal("5.00"),
            reason="Breakfast menu stock running low",
        )
        self.client.login(username="manager1", password="password")

        response = self.client.post(
            reverse("kitchen:ingredient_request_review", args=[ingredient_request.pk]),
            {
                "status": IngredientRequest.APPROVED,
                "manager_note": "Approved for next supplier order",
            },
        )

        self.assertEqual(response.status_code, 302)
        ingredient_request.refresh_from_db()
        self.assertEqual(ingredient_request.status, IngredientRequest.APPROVED)
        self.assertEqual(ingredient_request.reviewed_by, self.manager)
        self.assertIsNotNone(ingredient_request.reviewed_at)

    def test_kitchen_staff_only_sees_their_own_requests(self):
        other_kitchen_user = User.objects.create_user(
            username="kitchen2",
            password="password",
        )
        other_kitchen_user.profile.role = Profile.KITCHEN
        other_kitchen_user.profile.save()

        own_request = IngredientRequest.objects.create(
            ingredient=self.ingredient,
            requested_by=self.kitchen_user,
            quantity=Decimal("5.00"),
            reason="Own request",
        )
        other_request = IngredientRequest.objects.create(
            ingredient=self.ingredient,
            requested_by=other_kitchen_user,
            quantity=Decimal("3.00"),
            reason="Other request",
        )

        self.client.login(username="kitchen1", password="password")
        response = self.client.get(reverse("kitchen:ingredient_request_list"))

        self.assertEqual(response.status_code, 200)
        ingredient_requests = list(response.context["ingredient_requests"])
        self.assertIn(own_request, ingredient_requests)
        self.assertNotIn(other_request, ingredient_requests)
