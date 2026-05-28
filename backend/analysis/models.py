from django.conf import settings
from django.db import models


class Source(models.Model):
    class SourceType(models.TextChoices):
        SAP = "sap", "SAP"
        UTILITY = "utility", "Utility"
        TRAVEL = "travel", "Travel"

    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    client_name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_sources",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Entry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        FLAGGED = "flagged", "Flagged"
        APPROVED = "approved", "Approved"

    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="entries")
    label = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_entries",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_entries",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label
