from django.core.management.base import BaseCommand

from analysis.models import Entry, Source
from core.models import User


class Command(BaseCommand):
    help = "Seed demo users, sources, and entries"

    def handle(self, *args, **options):
        alice, created = User.objects.get_or_create(
            username="alice",
            defaults={"role": User.Role.ANALYST},
        )
        if created:
            alice.set_password("password123")
            alice.save()

        bob, created = User.objects.get_or_create(
            username="bob",
            defaults={"role": User.Role.ANALYST},
        )
        if created:
            bob.set_password("password123")
            bob.save()

        sap_source, _ = Source.objects.get_or_create(
            name="Acme SAP fuel export",
            defaults={
                "source_type": Source.SourceType.SAP,
                "client_name": "Acme Corp",
                "created_by": alice,
            },
        )
        utility_source, _ = Source.objects.get_or_create(
            name="Globex utility CSV",
            defaults={
                "source_type": Source.SourceType.UTILITY,
                "client_name": "Globex",
                "created_by": bob,
            },
        )
        travel_source, _ = Source.objects.get_or_create(
            name="Acme Concur travel pull",
            defaults={
                "source_type": Source.SourceType.TRAVEL,
                "client_name": "Acme Corp",
                "created_by": alice,
            },
        )

        Entry.objects.get_or_create(
            source=sap_source,
            label="Plant DE01 diesel 1200 L",
            defaults={"status": Entry.Status.NEW, "created_by": alice},
        )
        Entry.objects.get_or_create(
            source=sap_source,
            label="Procurement PO-8842 steel",
            defaults={"status": Entry.Status.FLAGGED, "created_by": alice},
        )
        Entry.objects.get_or_create(
            source=utility_source,
            label="Meter M-12 kWh 45000",
            defaults={"status": Entry.Status.APPROVED, "created_by": bob},
        )
        Entry.objects.get_or_create(
            source=travel_source,
            label="Flight DEL-BOM",
            defaults={"status": Entry.Status.NEW, "created_by": alice},
        )

        self.stdout.write(self.style.SUCCESS("Seeded demo data successfully."))
