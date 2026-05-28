from django.contrib import admin

from .models import Entry, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "source_type", "client_name", "created_by", "created_at")
    list_filter = ("source_type",)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "label",
        "source",
        "status",
        "created_by",
        "approved_by",
        "created_at",
    )
    list_filter = ("status", "source__source_type")
