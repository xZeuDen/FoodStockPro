from django.contrib.auth.models import User
from django.db import models


class IngredientCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    KG = "kg"
    GRAMS = "grams"
    LITRES = "litres"
    ML = "ml"
    UNITS = "units"
    BOXES = "boxes"

    UNIT_CHOICES = [
        (KG, "kg"),
        (GRAMS, "grams"),
        (LITRES, "litres"),
        (ML, "ml"),
        (UNITS, "units"),
        (BOXES, "boxes"),
    ]

    category = models.ForeignKey(
        IngredientCategory,
        on_delete=models.PROTECT,
        related_name="ingredients",
    )
    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=30, choices=UNIT_CHOICES)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_per_unit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"

    MOVEMENT_TYPES = [
        (IN, "In"),
        (OUT, "Out"),
        (ADJUSTMENT, "Adjustment"),
    ]

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingredient.name} - {self.get_movement_type_display()} - {self.quantity}"
