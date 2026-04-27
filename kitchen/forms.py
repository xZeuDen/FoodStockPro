from django import forms

from .models import IngredientRequest


class BootstrapFormMixin:
    """Add Bootstrap classes to form fields."""

    def add_bootstrap_classes(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})


class IngredientRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = IngredientRequest
        fields = ["ingredient", "quantity", "reason"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_bootstrap_classes()


class IngredientRequestReviewForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = IngredientRequest
        fields = ["status", "manager_note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (IngredientRequest.APPROVED, "Approved"),
            (IngredientRequest.REJECTED, "Rejected"),
            (IngredientRequest.FULFILLED, "Fulfilled"),
        ]
        self.add_bootstrap_classes()
