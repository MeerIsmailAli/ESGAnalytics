from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role", {"fields": ("role", "created_at")}),
    )
    readonly_fields = ("created_at",)
    list_display = ("id", "username", "email", "role", "is_staff")
