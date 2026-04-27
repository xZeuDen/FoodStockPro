from django.contrib import admin
from django.urls import include, path

from dashboard import views as dashboard_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard_views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("inventory/", include("inventory.urls")),
    path("purchasing/", include("purchasing.urls")),
    path("kitchen/", include("kitchen.urls")),
    path("dashboard/", include("dashboard.urls")),
]