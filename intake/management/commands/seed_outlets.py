import json
from pathlib import Path

from django.core.management.base import BaseCommand

from intake.models import Outlet

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "outlets.json"


class Command(BaseCommand):
    help = "Load the outlet list used by the assessment."

    def handle(self, *args, **options):
        rows = json.loads(FIXTURE.read_text())
        made = 0
        for r in rows:
            _, created = Outlet.objects.update_or_create(
                outlet_code=r["outlet_code"],
                defaults={"outlet_name": r["outlet_name"],
                          "route_code": r.get("route_code", "")},
            )
            made += int(created)
        self.stdout.write(f"{len(rows)} outlets processed, {made} created")
