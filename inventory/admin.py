from django.contrib import admin

from .models import Ingredient, IngredientCategory, StockMovement


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "description")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "unit",
        "current_stock",
        "minimum_stock",
        "cost_per_unit",
        "is_active",
    )
    search_fields = ("name", "category__name")
    list_filter = ("category", "unit", "is_active")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "movement_type", "quantity", "created_by", "created_at")
    search_fields = ("ingredient__name", "note")
    list_filter = ("movement_type", "created_at")
