# bars/management/commands/import_pintxos.py
import csv, uuid, decimal, pathlib, re
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date
from bars.models import Bar

def clean(text: str) -> str:
    return (text or "").strip()

def parse_price(raw: str):
    raw = clean(raw).replace("€", "").replace(",", ".")
    raw = re.sub(r"[^\d.]", "", raw)
    return decimal.Decimal(raw) if raw else None

class Command(BaseCommand):
    help = "Overwrite DB bars with records from a TSV file"

    def add_arguments(self, parser):
        parser.add_argument("tsv_path", type=pathlib.Path, help="Path to TSV file")

    def handle(self, *args, **opts):
        path: pathlib.Path = opts["tsv_path"]
        if not path.exists():
            raise CommandError(f"{path} not found")

        created, replaced = 0, 0
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for row in reader:
                name = clean(row["Name"])
                address = clean(row["Address"])

                # Delete any existing rows with same name+address
                qs = Bar.objects.filter(name=name, address=address)
                if qs.exists():
                    qs.delete()
                    replaced += 1

                Bar.objects.create(
                    id=uuid.uuid4(),
                    name=name,
                    address=address,
                    map_link=clean(row["Map Link"]),
                    specialties=clean(row["Specialties"]),
                    price_range=clean(row["Price Range"]),
                    cana_price=parse_price(row["Caña Price"]),
                    crowd_level=clean(row["Crowd Level"]),
                    last_visited=parse_date(clean(row["Last Visited"])) or None,
                    tags=clean(row["Tags"]),
                    notes=clean(row["Notes"]),
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created} bars (replaced {replaced} existing rows)"
            )
        )