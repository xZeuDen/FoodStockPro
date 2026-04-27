from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import Profile


def home(request):
    return render(request, "home.html")


@login_required
def dashboard_home(request):
    role = request.user.profile.role

    if role == Profile.MANAGER:
        return render(request, "dashboard/manager_dashboard.html")

    if role == Profile.KITCHEN:
        return render(request, "dashboard/kitchen_dashboard.html")

    if role == Profile.SUPPLIER:
        return render(request, "dashboard/supplier_dashboard.html")

    if role == Profile.FINANCE:
        return render(request, "dashboard/finance_dashboard.html")

    return redirect("home")
