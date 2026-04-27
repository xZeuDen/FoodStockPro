from django.urls import path

from . import views


app_name = "purchasing"

urlpatterns = [
    path("", views.purchase_order_list, name="purchase_order_list"),
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/", views.supplier_detail, name="supplier_detail"),
    path("suppliers/<int:pk>/edit/", views.supplier_update, name="supplier_update"),
    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list_alt"),
    path("purchase-orders/add/", views.purchase_order_create, name="purchase_order_create"),
    path("purchase-orders/<int:pk>/", views.purchase_order_detail, name="purchase_order_detail"),
    path("purchase-orders/<int:pk>/edit/", views.purchase_order_update, name="purchase_order_update"),
    path(
        "purchase-orders/<int:pk>/add-item/",
        views.purchase_order_item_create,
        name="purchase_order_item_create",
    ),
    path(
        "purchase-order-items/<int:pk>/edit/",
        views.purchase_order_item_update,
        name="purchase_order_item_update",
    ),
    path(
        "purchase-orders/<int:pk>/supplier-update/",
        views.supplier_order_update,
        name="supplier_order_update",
    ),
]
