from django.urls import path

from . import views


app_name = "kitchen"

urlpatterns = [
    path("", views.ingredient_request_list, name="ingredient_request_list"),
    path("requests/add/", views.ingredient_request_create, name="ingredient_request_create"),
    path(
        "requests/<int:pk>/",
        views.ingredient_request_detail,
        name="ingredient_request_detail",
    ),
    path(
        "requests/<int:pk>/review/",
        views.ingredient_request_review,
        name="ingredient_request_review",
    ),
]
