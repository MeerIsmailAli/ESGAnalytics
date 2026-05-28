from django.utils import timezone
from rest_framework import serializers

from .models import Entry, Source


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
            "created_by",
            "created_by_username",
            "entry_count",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

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
            "created_by",
            "created_by_username",
            "approved_by",
            "approved_by_username",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)
        if new_status == Entry.Status.APPROVED and instance.status != Entry.Status.APPROVED:
            instance.approved_by = self.context["request"].user
            instance.approved_at = timezone.now()
        elif new_status != Entry.Status.APPROVED:
            instance.approved_by = None
            instance.approved_at = None
        return super().update(instance, validated_data)
