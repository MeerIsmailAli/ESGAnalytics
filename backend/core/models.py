from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        ANALYST = "analyst", "Analyst"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ANALYST)
    created_at = models.DateTimeField(auto_now_add=True)
