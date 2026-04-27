from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from inventory.models import Ingredient, IngredientCategory, StockMovement

from .models import PurchaseOrder, PurchaseOrderItem, Supplier


class PurchasingTests(TestCase):
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
            current_stock=Decimal("10.00"),
            minimum_stock=Decimal("5.00"),
            cost_per_unit=Decimal("6.50"),
        )
        self.supplier = Supplier.objects.create(
            name="Fresh Foods Ltd",
            contact_name="Sarah Supplier",
            email="supplier@example.com",
            phone="0871111111",
        )
        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            created_by=self.manager,
            status=PurchaseOrder.SENT,
            notes="Test purchase order",
        )
        self.item = PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            ingredient=self.ingredient,
            quantity=Decimal("10.00"),
            unit_price=Decimal("6.50"),
        )

    def test_supplier_str_returns_name(self):
        self.assertEqual(str(self.supplier), "Fresh Foods Ltd")

    def test_purchase_order_total_cost_returns_correct_total(self):
        self.assertEqual(self.purchase_order.total_cost(), Decimal("65.0000"))

    def test_purchase_order_item_line_total_returns_correct_total(self):
        self.assertEqual(self.item.line_total(), Decimal("65.0000"))

    def test_manager_can_access_purchase_order_list_page(self):
        self.client.login(username="manager1", password="password")
        response = self.client.get(reverse("purchasing:purchase_order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Purchase Orders")

    def test_manager_can_create_purchase_order(self):
        self.client.login(username="manager1", password="password")

        response = self.client.post(
            reverse("purchasing:purchase_order_create"),
            {
                "supplier": self.supplier.id,
                "expected_delivery_date": "",
                "status": PurchaseOrder.DRAFT,
                "notes": "New test order",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PurchaseOrder.objects.count(), 2)

    def test_delivered_purchase_order_increases_stock(self):
        self.client.login(username="manager1", password="password")

        response = self.client.post(
            reverse("purchasing:purchase_order_update", args=[self.purchase_order.pk]),
            {
                "supplier": self.supplier.id,
                "expected_delivery_date": "",
                "status": PurchaseOrder.DELIVERED,
                "notes": "Delivered order",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.ingredient.refresh_from_db()
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.status, PurchaseOrder.DELIVERED)
        self.assertEqual(self.ingredient.current_stock, Decimal("20.00"))
        self.assertTrue(
            StockMovement.objects.filter(
                ingredient=self.ingredient,
                movement_type=StockMovement.IN,
                quantity=Decimal("10.00"),
            ).exists()
        )

    def test_already_delivered_purchase_order_does_not_increase_stock_twice(self):
        self.client.login(username="manager1", password="password")
        self.purchase_order.status = PurchaseOrder.DELIVERED
        self.purchase_order.save()

        response = self.client.post(
            reverse("purchasing:purchase_order_update", args=[self.purchase_order.pk]),
            {
                "supplier": self.supplier.id,
                "expected_delivery_date": "",
                "status": PurchaseOrder.DELIVERED,
                "notes": "Still delivered",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.current_stock, Decimal("10.00"))
