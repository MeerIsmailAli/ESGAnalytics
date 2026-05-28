from django.contrib import admin

from .models import AnalysisRecord


@admin.register(AnalysisRecord)
class AnalysisRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "tenant", "status", "created_by", "created_at")
    list_filter = ("tenant", "status")
    search_fields = ("title",)
