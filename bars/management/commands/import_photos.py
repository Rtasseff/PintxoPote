import csv
import pathlib
from django.core.management.base import BaseCommand
from bars.models import Bar, BarPhoto

PHOTO_CSV = pathlib.Path("photo_map.csv")  # adjust if it's in a subfolder
UPLOAD_SUBFOLDER = "bars/"  # relative to MEDIA_ROOT

class Command(BaseCommand):
    help = "Import bar photos from photo_map.csv and link to BarPhoto model"

    def handle(self, *args, **options):
        if not PHOTO_CSV.exists():
            self.stderr.write(f"Missing {PHOTO_CSV}")
            return

        with PHOTO_CSV.open() as fh:
            reader = csv.DictReader(fh)
            created_count = 0
            skipped_count = 0
            for row in reader:
                bar_name = row["Name"]
                filename = row["Filename"]
                bar = Bar.objects.filter(name=bar_name).first()
                if not bar:
                    self.stderr.write(f"Bar not found: {bar_name}")
                    skipped_count += 1
                    continue

                rel_path = UPLOAD_SUBFOLDER + filename
                photo, created = BarPhoto.objects.get_or_create(
                    bar=bar,
                    image=rel_path,
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Linked {created_count} photos. Skipped {skipped_count} (unmatched bar names)."
        ))
