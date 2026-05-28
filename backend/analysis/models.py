from django.conf import settings
from django.db import models

from core.models import Tenant


class AnalysisRecord(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        FLAGGED = "flagged", "Flagged"
        APPROVED = "approved", "Approved"

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="analysis_records"
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_analysis_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.slug} - {self.title}"
