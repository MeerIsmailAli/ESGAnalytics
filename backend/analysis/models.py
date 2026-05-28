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
    filename = models.CharField(max_length=255, blank=True)
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

    class Scope(models.TextChoices):
        SCOPE_1 = "1", "Scope 1"
        SCOPE_2 = "2", "Scope 2"
        SCOPE_3 = "3", "Scope 3"

    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="entries")
    label = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    scope = models.CharField(max_length=1, choices=Scope.choices, default=Scope.SCOPE_1)
    activity_type = models.CharField(max_length=64, blank=True)

    quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=32, blank=True)
    normalized_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, null=True, blank=True
    )
    normalized_unit = models.CharField(max_length=32, blank=True)
    emissions_kg_co2e = models.DecimalField(
        max_digits=14, decimal_places=4, null=True, blank=True
    )

    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    external_id = models.CharField(max_length=128, blank=True)

    raw_data = models.JSONField(default=dict, blank=True)
    is_suspicious = models.BooleanField(default=False)
    suspicion_reason = models.CharField(max_length=255, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_entries",
    )
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="flagged_entries",
    )
    flagged_at = models.DateTimeField(null=True, blank=True)
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


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        FLAGGED = "flagged", "Flagged"
        APPROVED = "approved", "Approved"
        DELETED = "deleted", "Deleted"
        INGESTED = "ingested", "Ingested"

    entry = models.ForeignKey(
        Entry, on_delete=models.CASCADE, related_name="audit_logs", null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
