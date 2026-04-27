from django.urls import path

from . import views


app_name = "inventory"

urlpatterns = [
    path("", views.ingredient_list, name="ingredient_list"),
    path("ingredients/<int:pk>/", views.ingredient_detail, name="ingredient_detail"),
    path("ingredients/add/", views.ingredient_create, name="ingredient_create"),
    path("ingredients/<int:pk>/edit/", views.ingredient_update, name="ingredient_update"),
    path("categories/", views.category_list, name="category_list"),
    path("stock-movements/", views.stock_movement_list, name="stock_movement_list"),
    path("stock-movements/add/", views.stock_movement_create, name="stock_movement_create"),
]
