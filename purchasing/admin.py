from django.contrib import admin

from .models import PurchaseOrder, PurchaseOrderItem, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "email", "phone", "is_active", "created_at")
    search_fields = ("name", "contact_name", "email", "phone")
    list_filter = ("is_active", "created_at")


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "supplier",
        "created_by",
        "order_date",
        "expected_delivery_date",
        "status",
        "total_cost",
    )
    search_fields = ("supplier__name", "notes")
    list_filter = ("status", "order_date", "expected_delivery_date")
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ("purchase_order", "ingredient", "quantity", "unit_price", "line_total")
    search_fields = ("purchase_order__supplier__name", "ingredient__name")
    list_filter = ("ingredient",)
