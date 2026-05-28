from django.contrib import admin

from .models import AuditLog, Entry, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "source_type", "client_name", "filename", "created_at")
    list_filter = ("source_type",)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "label",
        "source",
        "scope",
        "status",
        "emissions_kg_co2e",
        "is_suspicious",
        "created_at",
    )
    list_filter = ("status", "scope", "is_suspicious", "source__source_type")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "entry", "user", "action", "note", "created_at")
    list_filter = ("action",)
