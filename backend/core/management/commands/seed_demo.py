from django.core.management.base import BaseCommand

from analysis.models import AnalysisRecord
from core.models import Tenant, User


class Command(BaseCommand):
    help = "Seed demo tenants, users, and analysis records"

    def handle(self, *args, **options):
        acme, _ = Tenant.objects.get_or_create(name="Acme Corp", slug="acme-corp")
        globex, _ = Tenant.objects.get_or_create(name="Globex", slug="globex")

        alice, created = User.objects.get_or_create(
            username="alice",
            defaults={"tenant": acme, "role": User.Role.ANALYST},
        )
        if created:
            alice.set_password("password123")
            alice.save()

        bob, created = User.objects.get_or_create(
            username="bob",
            defaults={"tenant": globex, "role": User.Role.ANALYST},
        )
        if created:
            bob.set_password("password123")
            bob.save()

        AnalysisRecord.objects.get_or_create(
            tenant=acme,
            title="Q1 electricity review",
            defaults={"status": AnalysisRecord.Status.FLAGGED, "created_by": alice},
        )
        AnalysisRecord.objects.get_or_create(
            tenant=acme,
            title="Fleet fuel check",
            defaults={"status": AnalysisRecord.Status.NEW, "created_by": alice},
        )
        AnalysisRecord.objects.get_or_create(
            tenant=globex,
            title="Travel spend audit",
            defaults={"status": AnalysisRecord.Status.APPROVED, "created_by": bob},
        )
        AnalysisRecord.objects.get_or_create(
            tenant=globex,
            title="Facility baseline import",
            defaults={"status": AnalysisRecord.Status.NEW, "created_by": bob},
        )

        self.stdout.write(self.style.SUCCESS("Seeded demo data successfully."))
