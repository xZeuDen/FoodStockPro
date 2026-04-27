from django import forms

from .models import Ingredient, IngredientCategory, StockMovement


class BootstrapFormMixin:
    """Add Bootstrap classes to fields in a beginner-friendly way."""

    def add_bootstrap_classes(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-check-input"})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})


class IngredientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            "category",
            "name",
            "unit",
            "current_stock",
            "minimum_stock",
            "cost_per_unit",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_bootstrap_classes()


class IngredientCategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = IngredientCategory
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_bootstrap_classes()


class StockMovementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["ingredient", "movement_type", "quantity", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_bootstrap_classes()
