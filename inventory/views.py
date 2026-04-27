from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Profile

from .forms import IngredientCategoryForm, IngredientForm, StockMovementForm
from .models import Ingredient, IngredientCategory, StockMovement


def user_has_inventory_access(user):
    return user.profile.role in [Profile.MANAGER, Profile.KITCHEN]


def redirect_without_permission(request):
    messages.error(request, "You do not have permission to manage inventory.")
    return redirect("dashboard:home")


@login_required
def ingredient_list(request):
    query = request.GET.get("q", "")
    ingredients = Ingredient.objects.filter(is_active=True).select_related("category")

    if query:
        ingredients = ingredients.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        )

    ingredients = sorted(ingredients, key=lambda ingredient: not ingredient.is_low_stock())

    return render(
        request,
        "inventory/ingredient_list.html",
        {"ingredients": ingredients, "query": query},
    )


@login_required
def ingredient_detail(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    stock_movements = ingredient.stock_movements.select_related("created_by").order_by(
        "-created_at"
    )[:10]

    return render(
        request,
        "inventory/ingredient_detail.html",
        {"ingredient": ingredient, "stock_movements": stock_movements},
    )


@login_required
def ingredient_create(request):
    if not user_has_inventory_access(request.user):
        return redirect_without_permission(request)

    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ingredient created successfully.")
            return redirect("inventory:ingredient_list")
    else:
        form = IngredientForm()

    return render(
        request,
        "inventory/ingredient_form.html",
        {"form": form, "title": "Add Ingredient"},
    )


@login_required
def ingredient_update(request, pk):
    if not user_has_inventory_access(request.user):
        return redirect_without_permission(request)

    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == "POST":
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            messages.success(request, "Ingredient updated successfully.")
            return redirect("inventory:ingredient_detail", pk=ingredient.pk)
    else:
        form = IngredientForm(instance=ingredient)

    return render(
        request,
        "inventory/ingredient_form.html",
        {"form": form, "title": "Edit Ingredient"},
    )


@login_required
def category_list(request):
    categories = IngredientCategory.objects.annotate(
        ingredient_count=Count("ingredients")
    ).order_by("name")

    if request.method == "POST":
        if not user_has_inventory_access(request.user):
            return redirect_without_permission(request)

        form = IngredientCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("inventory:category_list")
    else:
        form = IngredientCategoryForm()

    return render(
        request,
        "inventory/category_list.html",
        {"categories": categories, "form": form},
    )


@login_required
def stock_movement_list(request):
    stock_movements = StockMovement.objects.select_related(
        "ingredient", "created_by"
    ).order_by("-created_at")

    return render(
        request,
        "inventory/stock_movement_list.html",
        {"stock_movements": stock_movements},
    )


@login_required
def stock_movement_create(request):
    if not user_has_inventory_access(request.user):
        return redirect_without_permission(request)

    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            stock_movement = form.save(commit=False)
            stock_movement.created_by = request.user
            stock_movement.save()

            ingredient = stock_movement.ingredient
            if stock_movement.movement_type == StockMovement.OUT:
                ingredient.current_stock -= stock_movement.quantity
            else:
                ingredient.current_stock += stock_movement.quantity
            ingredient.save()

            messages.success(request, "Stock movement recorded successfully.")
            return redirect("inventory:stock_movement_list")
    else:
        form = StockMovementForm()

    return render(
        request,
        "inventory/ingredient_form.html",
        {"form": form, "title": "Add Stock Movement"},
    )
