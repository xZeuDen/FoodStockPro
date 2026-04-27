from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from inventory.models import Ingredient, IngredientCategory, StockMovement
from kitchen.models import IngredientRequest
from purchasing.models import PurchaseOrder, PurchaseOrderItem, Supplier


class Command(BaseCommand):
    help = "Create sample data for the FoodStockPro project."

    def handle(self, *args, **options):
        self.stdout.write("Seeding FoodStockPro sample data...")

        users = self.create_users()
        categories = self.create_categories()
        ingredients = self.create_ingredients(categories)
        suppliers = self.create_suppliers()

        self.clear_sample_transactions(users, ingredients, suppliers)
        self.create_stock_movements(users, ingredients)
        self.create_purchase_orders(users, ingredients, suppliers)
        self.create_kitchen_requests(users, ingredients)

        self.stdout.write(self.style.SUCCESS("FoodStockPro sample data created successfully."))
        self.stdout.write(self.style.SUCCESS("All sample user passwords are: password"))

    def create_users(self):
        user_data = [
            {
                "username": "admin",
                "email": "admin@admin.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
                "role": Profile.MANAGER,
            },
            {
                "username": "manager1",
                "email": "manager1@foodstockpro.com",
                "first_name": "Maria",
                "last_name": "Manager",
                "role": Profile.MANAGER,
            },
            {
                "username": "kitchen1",
                "email": "kitchen1@foodstockpro.com",
                "first_name": "Kevin",
                "last_name": "Chef",
                "role": Profile.KITCHEN,
            },
            {
                "username": "supplier1",
                "email": "supplier1@freshfoods.com",
                "first_name": "Sarah",
                "last_name": "Supplier",
                "role": Profile.SUPPLIER,
            },
            {
                "username": "finance1",
                "email": "finance1@foodstockpro.com",
                "first_name": "Fiona",
                "last_name": "Finance",
                "role": Profile.FINANCE,
            },
        ]

        users = {}
        for data in user_data:
            role = data.pop("role")
            user, created = User.objects.update_or_create(
                username=data["username"],
                defaults=data,
            )
            user.set_password("password")
            user.save()

            user.profile.role = role
            user.profile.save()
            users[user.username] = user

            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} user: {user.username}")

        return users

    def create_categories(self):
        category_names = ["Meat", "Vegetables", "Dairy", "Dry Goods", "Drinks"]
        categories = {}

        for name in category_names:
            category, created = IngredientCategory.objects.get_or_create(name=name)
            categories[name] = category

            action = "Created" if created else "Found"
            self.stdout.write(f"{action} category: {name}")

        return categories

    def create_ingredients(self, categories):
        ingredient_data = [
            ("Chicken Fillet", "Meat", Ingredient.KG, 10, 5, "6.50"),
            ("Potatoes", "Vegetables", Ingredient.KG, 25, 10, "1.20"),
            ("Milk", "Dairy", Ingredient.LITRES, 8, 12, "1.10"),
            ("Pasta", "Dry Goods", Ingredient.KG, 15, 6, "2.30"),
            ("Orange Juice", "Drinks", Ingredient.LITRES, 4, 8, "1.90"),
        ]

        ingredients = {}
        for name, category_name, unit, current_stock, minimum_stock, cost_per_unit in ingredient_data:
            ingredient, created = Ingredient.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[category_name],
                    "unit": unit,
                    "current_stock": current_stock,
                    "minimum_stock": minimum_stock,
                    "cost_per_unit": cost_per_unit,
                    "is_active": True,
                },
            )
            ingredients[name] = ingredient

            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} ingredient: {name}")

        return ingredients

    def create_suppliers(self):
        supplier_data = [
            {
                "name": "Fresh Foods Ltd",
                "contact_name": "Sarah Supplier",
                "email": "supplier1@freshfoods.com",
                "phone": "0871111111",
                "address": "Dublin Food Market",
            },
            {
                "name": "Green Farm Produce",
                "contact_name": "John Green",
                "email": "orders@greenfarm.com",
                "phone": "0872222222",
                "address": "Laois Farm Road",
            },
        ]

        suppliers = {}
        for data in supplier_data:
            supplier, created = Supplier.objects.update_or_create(
                email=data["email"],
                defaults={**data, "is_active": True},
            )
            suppliers[supplier.name] = supplier

            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} supplier: {supplier.name}")

        return suppliers

    def clear_sample_transactions(self, users, ingredients, suppliers):
        sample_purchase_orders = PurchaseOrder.objects.filter(
            supplier__in=suppliers.values(),
            created_by=users["manager1"],
        )
        PurchaseOrderItem.objects.filter(purchase_order__in=sample_purchase_orders).delete()
        sample_purchase_orders.delete()

        IngredientRequest.objects.filter(
            requested_by=users["kitchen1"],
            ingredient__in=ingredients.values(),
        ).delete()

        StockMovement.objects.filter(
            ingredient__in=ingredients.values(),
            note__in=[
                "Initial stock",
                "Stock received from PO-1",
                "Stock received from PO-2",
            ],
        ).delete()

        self.stdout.write("Cleared existing sample transactions.")

    def create_stock_movements(self, users, ingredients):
        stock_data = [
            ("Chicken Fillet", StockMovement.IN, 10, "Initial stock"),
            ("Potatoes", StockMovement.IN, 25, "Initial stock"),
            ("Milk", StockMovement.IN, 8, "Initial stock"),
            ("Pasta", StockMovement.IN, 15, "Initial stock"),
            ("Orange Juice", StockMovement.IN, 4, "Initial stock"),
        ]

        for ingredient_name, movement_type, quantity, note in stock_data:
            StockMovement.objects.create(
                ingredient=ingredients[ingredient_name],
                movement_type=movement_type,
                quantity=quantity,
                note=note,
                created_by=users["manager1"],
            )
            self.stdout.write(f"Created stock movement: {ingredient_name} {movement_type} {quantity}")

    def create_purchase_orders(self, users, ingredients, suppliers):
        fresh_foods_order = PurchaseOrder.objects.create(
            supplier=suppliers["Fresh Foods Ltd"],
            created_by=users["manager1"],
            status=PurchaseOrder.SENT,
            notes="Weekly meat and dairy order",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=fresh_foods_order,
            ingredient=ingredients["Chicken Fillet"],
            quantity=10,
            unit_price="6.50",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=fresh_foods_order,
            ingredient=ingredients["Milk"],
            quantity=12,
            unit_price="1.10",
        )
        self.stdout.write(f"Created purchase order: PO-{fresh_foods_order.id}")

        green_farm_order = PurchaseOrder.objects.create(
            supplier=suppliers["Green Farm Produce"],
            created_by=users["manager1"],
            status=PurchaseOrder.DELIVERED,
            notes="Vegetable stock delivery",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=green_farm_order,
            ingredient=ingredients["Potatoes"],
            quantity=20,
            unit_price="1.20",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=green_farm_order,
            ingredient=ingredients["Orange Juice"],
            quantity=10,
            unit_price="1.90",
        )
        self.stdout.write(f"Created purchase order: PO-{green_farm_order.id}")

    def create_kitchen_requests(self, users, ingredients):
        IngredientRequest.objects.create(
            ingredient=ingredients["Milk"],
            requested_by=users["kitchen1"],
            quantity=5,
            reason="Breakfast menu stock running low",
            status=IngredientRequest.PENDING,
        )
        self.stdout.write("Created kitchen request: Milk")

        IngredientRequest.objects.create(
            ingredient=ingredients["Chicken Fillet"],
            requested_by=users["kitchen1"],
            quantity=8,
            reason="Needed for lunch special",
            status=IngredientRequest.APPROVED,
            reviewed_by=users["manager1"],
            manager_note="Approved for next supplier order",
            reviewed_at=timezone.now(),
        )
        self.stdout.write("Created kitchen request: Chicken Fillet")
