from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("public/", views.home, name="public_home"),
]
