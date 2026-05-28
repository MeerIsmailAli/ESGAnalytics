from django.utils import timezone
from rest_framework import serializers

from .models import AuditLog, Entry, Source


class SourceSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    entry_count = serializers.SerializerMethodField()

    class Meta:
        model = Source
        fields = [
            "id",
            "name",
            "source_type",
            "client_name",
            "filename",
            "created_by",
            "created_by_username",
            "entry_count",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at", "filename"]

    def get_entry_count(self, obj):
        return obj.entries.count()

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class EntrySerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    source_type = serializers.CharField(source="source.source_type", read_only=True)
    client_name = serializers.CharField(source="source.client_name", read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    flagged_by_username = serializers.CharField(
        source="flagged_by.username", read_only=True
    )
    approved_by_username = serializers.CharField(
        source="approved_by.username", read_only=True
    )

    class Meta:
        model = Entry
        fields = [
            "id",
            "source",
            "source_name",
            "source_type",
            "client_name",
            "label",
            "status",
            "scope",
            "activity_type",
            "quantity",
            "unit",
            "normalized_quantity",
            "normalized_unit",
            "emissions_kg_co2e",
            "period_start",
            "period_end",
            "external_id",
            "is_suspicious",
            "suspicion_reason",
            "created_by",
            "created_by_username",
            "flagged_by",
            "flagged_by_username",
            "flagged_at",
            "approved_by",
            "approved_by_username",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "flagged_by",
            "flagged_at",
            "approved_by",
            "approved_at",
            "emissions_kg_co2e",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        new_status = validated_data.get("status", instance.status)

        if new_status == Entry.Status.FLAGGED and instance.status != Entry.Status.FLAGGED:
            instance.flagged_by = user
            instance.flagged_at = timezone.now()
            AuditLog.objects.create(
                entry=instance, user=user, action=AuditLog.Action.FLAGGED
            )
        elif new_status == Entry.Status.APPROVED and instance.status != Entry.Status.APPROVED:
            instance.approved_by = user
            instance.approved_at = timezone.now()
            AuditLog.objects.create(
                entry=instance, user=user, action=AuditLog.Action.APPROVED
            )
        elif new_status == Entry.Status.NEW:
            instance.flagged_by = None
            instance.flagged_at = None
            instance.approved_by = None
            instance.approved_at = None

        return super().update(instance, validated_data)


class UploadSerializer(serializers.Serializer):
    source_type = serializers.ChoiceField(choices=Source.SourceType.choices)
    client_name = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    file = serializers.FileField()
