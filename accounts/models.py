from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    MANAGER = "MANAGER"
    KITCHEN = "KITCHEN"
    SUPPLIER = "SUPPLIER"
    FINANCE = "FINANCE"

    ROLE_CHOICES = [
        (MANAGER, "Manager"),
        (KITCHEN, "Kitchen Staff"),
        (SUPPLIER, "Supplier"),
        (FINANCE, "Finance Officer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MANAGER)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile automatically whenever a new user is created."""
    if created:
        Profile.objects.create(user=instance)
