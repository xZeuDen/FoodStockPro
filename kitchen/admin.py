from django.contrib import admin

from .models import IngredientRequest


@admin.register(IngredientRequest)
class IngredientRequestAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "quantity",
        "requested_by",
        "status",
        "reviewed_by",
        "created_at",
    )
    list_filter = ("status", "created_at", "reviewed_at")
    search_fields = (
        "ingredient__name",
        "requested_by__username",
        "reviewed_by__username",
        "reason",
        "manager_note",
    )
