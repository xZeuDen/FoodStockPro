from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Profile
from inventory.models import StockMovement

from .forms import (
    PurchaseOrderForm,
    PurchaseOrderItemForm,
    SupplierForm,
    SupplierOrderStatusForm,
)
from .models import PurchaseOrder, PurchaseOrderItem, Supplier


def get_user_role(user):
    try:
        return user.profile.role
    except Profile.DoesNotExist:
        return None


def user_is_manager_or_finance(user):
    return get_user_role(user) in [Profile.MANAGER, Profile.FINANCE]


def user_is_supplier(user):
    return get_user_role(user) == Profile.SUPPLIER


def user_can_manage_purchasing(user):
    return user_is_manager_or_finance(user)


def user_is_manager(user):
    return get_user_role(user) == Profile.MANAGER


def redirect_without_permission(request):
    messages.error(request, "You do not have permission to access this purchasing page.")
    return redirect("dashboard:home")


def update_stock_from_delivered_po(purchase_order, user):
    """Add delivered purchase order item quantities into inventory stock."""
    for item in purchase_order.items.select_related("ingredient").all():
        ingredient = item.ingredient
        ingredient.current_stock += item.quantity
        ingredient.save()

        StockMovement.objects.create(
            ingredient=ingredient,
            movement_type=StockMovement.IN,
            quantity=item.quantity,
            note=f"Stock received from PO-{purchase_order.id}",
            created_by=user,
        )


@login_required
def supplier_list(request):
    if not user_is_manager_or_finance(request.user):
        return redirect_without_permission(request)

    suppliers = Supplier.objects.filter(is_active=True).order_by("name")
    return render(
        request,
        "purchasing/supplier_list.html",
        {"suppliers": suppliers, "user_role": get_user_role(request.user)},
    )


@login_required
def supplier_detail(request, pk):
    if not user_is_manager_or_finance(request.user):
        return redirect_without_permission(request)

    supplier = get_object_or_404(Supplier, pk=pk)
    purchase_orders = supplier.purchase_orders.order_by("-created_at")
    return render(
        request,
        "purchasing/supplier_detail.html",
        {
            "supplier": supplier,
            "purchase_orders": purchase_orders,
            "user_role": get_user_role(request.user),
        },
    )


@login_required
def supplier_create(request):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, "Supplier created successfully.")
            return redirect("purchasing:supplier_detail", pk=supplier.pk)
    else:
        form = SupplierForm()

    return render(
        request,
        "purchasing/supplier_form.html",
        {"form": form, "title": "Add Supplier", "cancel_url": "purchasing:supplier_list"},
    )


@login_required
def supplier_update(request, pk):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect("purchasing:supplier_detail", pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)

    return render(
        request,
        "purchasing/supplier_form.html",
        {
            "form": form,
            "title": "Edit Supplier",
            "supplier": supplier,
            "cancel_url": "purchasing:supplier_detail",
        },
    )


@login_required
def purchase_order_list(request):
    role = get_user_role(request.user)

    if role == Profile.KITCHEN:
        return redirect_without_permission(request)

    if not user_is_manager_or_finance(request.user) and not user_is_supplier(request.user):
        return redirect_without_permission(request)

    purchase_orders = PurchaseOrder.objects.select_related("supplier", "created_by").order_by(
        "-created_at"
    )
    return render(
        request,
        "purchasing/purchase_order_list.html",
        {"purchase_orders": purchase_orders, "user_role": role},
    )


@login_required
def purchase_order_detail(request, pk):
    if not user_is_manager_or_finance(request.user) and not user_is_supplier(request.user):
        return redirect_without_permission(request)

    purchase_order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "created_by"),
        pk=pk,
    )
    items = purchase_order.items.select_related("ingredient")
    role = get_user_role(request.user)

    return render(
        request,
        "purchasing/purchase_order_detail.html",
        {
            "purchase_order": purchase_order,
            "items": items,
            "user_role": role,
            "is_manager": role == Profile.MANAGER,
            "is_supplier": role == Profile.SUPPLIER,
        },
    )


@login_required
def purchase_order_create(request):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            purchase_order = form.save(commit=False)
            purchase_order.created_by = request.user
            purchase_order.save()
            messages.success(request, "Purchase order created successfully.")
            return redirect("purchasing:purchase_order_detail", pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm()

    return render(
        request,
        "purchasing/purchase_order_form.html",
        {"form": form, "title": "Add Purchase Order"},
    )


@login_required
def purchase_order_update(request, pk):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        old_status = purchase_order.status
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        if form.is_valid():
            purchase_order = form.save()
            if old_status != PurchaseOrder.DELIVERED and purchase_order.status == PurchaseOrder.DELIVERED:
                update_stock_from_delivered_po(purchase_order, request.user)
                messages.success(request, "Purchase order delivered. Inventory stock was updated.")
            messages.success(request, "Purchase order updated successfully.")
            return redirect("purchasing:purchase_order_detail", pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm(instance=purchase_order)

    return render(
        request,
        "purchasing/purchase_order_form.html",
        {"form": form, "title": "Edit Purchase Order", "purchase_order": purchase_order},
    )


@login_required
def purchase_order_item_create(request, pk):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        form = PurchaseOrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = purchase_order
            item.save()
            messages.success(request, "Purchase order item added successfully.")
            return redirect("purchasing:purchase_order_detail", pk=purchase_order.pk)
    else:
        form = PurchaseOrderItemForm()

    return render(
        request,
        "purchasing/purchase_order_item_form.html",
        {"form": form, "title": "Add Purchase Order Item", "purchase_order": purchase_order},
    )


@login_required
def purchase_order_item_update(request, pk):
    if not user_is_manager(request.user):
        return redirect_without_permission(request)

    item = get_object_or_404(PurchaseOrderItem, pk=pk)
    if request.method == "POST":
        form = PurchaseOrderItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase order item updated successfully.")
            return redirect("purchasing:purchase_order_detail", pk=item.purchase_order.pk)
    else:
        form = PurchaseOrderItemForm(instance=item)

    return render(
        request,
        "purchasing/purchase_order_item_form.html",
        {
            "form": form,
            "title": "Edit Purchase Order Item",
            "purchase_order": item.purchase_order,
        },
    )


@login_required
def supplier_order_update(request, pk):
    if not user_is_supplier(request.user):
        return redirect_without_permission(request)

    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        old_status = purchase_order.status
        form = SupplierOrderStatusForm(request.POST, instance=purchase_order)
        if form.is_valid():
            purchase_order = form.save()
            if old_status != PurchaseOrder.DELIVERED and purchase_order.status == PurchaseOrder.DELIVERED:
                update_stock_from_delivered_po(purchase_order, request.user)
                messages.success(request, "Purchase order delivered. Inventory stock was updated.")
            messages.success(request, "Purchase order status updated successfully.")
            return redirect("purchasing:purchase_order_detail", pk=purchase_order.pk)
    else:
        form = SupplierOrderStatusForm(instance=purchase_order)

    return render(
        request,
        "purchasing/supplier_order_update.html",
        {"form": form, "purchase_order": purchase_order},
    )
