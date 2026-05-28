from pathlib import Path

from django.core.management.base import BaseCommand

from analysis.models import Entry, Source
from analysis.services import ingest_file
from core.models import User

DEMO_PASSWORD = "password123"
SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_files"


class Command(BaseCommand):
    help = "Seed demo users and load sample ingestion files"

    def _ensure_user(self, username, role):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"role": role},
        )
        user.set_password(DEMO_PASSWORD)
        user.role = role
        user.save()
        return user

    def _ingest_sample(self, path, source_type, client_name, user):
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Missing sample: {path}"))
            return
        with open(path, "rb") as f:
            data = f.read()
        result, err = ingest_file(
            source_type=source_type,
            file_bytes=data,
            source_name=f"Sample {path.name}",
            client_name=client_name,
            user=user,
            filename=path.name,
        )
        if err:
            self.stdout.write(self.style.ERROR(f"{path.name}: {err}"))
        else:
            self.stdout.write(f"  {path.name}: {result['created']} entries")

    def handle(self, *args, **options):
        alice = self._ensure_user("alice", User.Role.ANALYST)
        self._ensure_user("bob", User.Role.ANALYST)

        # Clear old demo entries/sources so re-seed is predictable
        Entry.objects.all().delete()
        Source.objects.all().delete()

        self.stdout.write("Loading sample files...")
        self._ingest_sample(
            SAMPLE_DIR / "sap_acme.csv", Source.SourceType.SAP, "Acme Corp", alice
        )
        self._ingest_sample(
            SAMPLE_DIR / "utility_globex.csv",
            Source.SourceType.UTILITY,
            "Globex",
            alice,
        )
        self._ingest_sample(
            SAMPLE_DIR / "travel_acme.json",
            Source.SourceType.TRAVEL,
            "Acme Corp",
            alice,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Done. Login: alice / password123 — includes SAP, utility, travel samples."
            )
        )
