from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Profile

from .forms import IngredientRequestForm, IngredientRequestReviewForm
from .models import IngredientRequest


def get_user_role(user):
    try:
        return user.profile.role
    except Profile.DoesNotExist:
        return None


def user_is_kitchen(user):
    return get_user_role(user) == Profile.KITCHEN


def user_is_manager(user):
    return get_user_role(user) == Profile.MANAGER


def user_can_view_requests(user):
    return user_is_manager(user) or user_is_kitchen(user)


def redirect_without_permission(request):
    messages.error(request, "You do not have permission to access kitchen requests.")
    return redirect("dashboard:home")


def user_can_view_request(user, ingredient_request):
    if user_is_manager(user):
        return True

    if user_is_kitchen(user):
        return ingredient_request.requested_by == user

    return False


@login_required
def ingredient_request_list(request):
    if not user_can_view_requests(request.user):
        return redirect_without_permission(request)

    if user_is_manager(request.user):
        ingredient_requests = IngredientRequest.objects.select_related(
            "ingredient", "requested_by"
        ).order_by("-created_at")
    else:
        ingredient_requests = IngredientRequest.objects.select_related(
            "ingredient", "requested_by"
        ).filter(requested_by=request.user).order_by("-created_at")

    return render(
        request,
        "kitchen/ingredient_request_list.html",
        {
            "ingredient_requests": ingredient_requests,
            "user_role": get_user_role(request.user),
        },
    )


@login_required
def ingredient_request_detail(request, pk):
    ingredient_request = get_object_or_404(
        IngredientRequest.objects.select_related(
            "ingredient", "requested_by", "reviewed_by"
        ),
        pk=pk,
    )

    if not user_can_view_request(request.user, ingredient_request):
        return redirect_without_permission(request)

    return render(
        request,
        "kitchen/ingredient_request_detail.html",
        {
            "ingredient_request": ingredient_request,
            "user_role": get_user_role(request.user),
        },
    )


@login_required
def ingredient_request_create(request):
    if not user_is_kitchen(request.user):
        return redirect_without_permission(request)

    if request.method == "POST":
        form = IngredientRequestForm(request.POST)
        if form.is_valid():
            ingredient_request = form.save(commit=False)
            ingredient_request.requested_by = request.user
            ingredient_request.status = IngredientRequest.PENDING
            ingredient_request.save()
            messages.success(request, "Ingredient request created successfully.")
            return redirect(
                "kitchen:ingredient_request_detail",
                pk=ingredient_request.pk,
            )
    else:
        form = IngredientRequestForm()

    return render(
        request,
        "kitchen/ingredient_request_form.html",
        {"form": form},
    )


@login_required
def ingredient_request_review(request, pk):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    ingredient_request = get_object_or_404(IngredientRequest, pk=pk)

    if request.method == "POST":
        form = IngredientRequestReviewForm(request.POST, instance=ingredient_request)
        if form.is_valid():
            reviewed_request = form.save(commit=False)
            reviewed_request.reviewed_by = request.user
            reviewed_request.reviewed_at = timezone.now()
            reviewed_request.save()
            messages.success(request, "Ingredient request reviewed successfully.")
            return redirect(
                "kitchen:ingredient_request_detail",
                pk=reviewed_request.pk,
            )
    else:
        form = IngredientRequestReviewForm(instance=ingredient_request)

    return render(
        request,
        "kitchen/ingredient_request_review.html",
        {"form": form, "ingredient_request": ingredient_request},
    )
