from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile

from .models import Ingredient, IngredientCategory, StockMovement


class InventoryTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager1",
            password="password",
        )
        self.manager.profile.role = Profile.MANAGER
        self.manager.profile.save()

        self.category = IngredientCategory.objects.create(name="Meat")
        self.ingredient = Ingredient.objects.create(
            category=self.category,
            name="Chicken Fillet",
            unit=Ingredient.KG,
            current_stock=Decimal("4.00"),
            minimum_stock=Decimal("5.00"),
            cost_per_unit=Decimal("6.50"),
        )

    def test_ingredient_str_returns_name(self):
        self.assertEqual(str(self.ingredient), "Chicken Fillet")

    def test_is_low_stock_returns_true_when_stock_is_low(self):
        self.assertTrue(self.ingredient.is_low_stock())

    def test_ingredient_list_page_requires_login(self):
        response = self.client.get(reverse("inventory:ingredient_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_manager_can_access_ingredient_list_page(self):
        self.client.login(username="manager1", password="password")
        response = self.client.get(reverse("inventory:ingredient_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chicken Fillet")

    def test_stock_movement_increases_ingredient_stock(self):
        self.client.login(username="manager1", password="password")

        response = self.client.post(
            reverse("inventory:stock_movement_create"),
            {
                "ingredient": self.ingredient.id,
                "movement_type": StockMovement.IN,
                "quantity": "3.00",
                "note": "Test stock increase",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.current_stock, Decimal("7.00"))
        self.assertTrue(
            StockMovement.objects.filter(
                ingredient=self.ingredient,
                movement_type=StockMovement.IN,
                quantity=Decimal("3.00"),
            ).exists()
        )
