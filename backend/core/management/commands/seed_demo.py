from django.core.management.base import BaseCommand

from analysis.models import Entry, Source
from core.models import User

DEMO_PASSWORD = "password123"


class Command(BaseCommand):
    help = "Seed demo users, sources, and entries"

    def _ensure_user(self, username, role):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"role": role},
        )
        # Always reset password so redeploys fix broken demo logins
        user.set_password(DEMO_PASSWORD)
        user.role = role
        user.save()
        return user

    def handle(self, *args, **options):
        alice = self._ensure_user("alice", User.Role.ANALYST)
        bob = self._ensure_user("bob", User.Role.ANALYST)

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

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded demo data. Login: alice / password123 (or bob / password123)"
            )
        )
