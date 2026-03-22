from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from PIL import Image


class Command(BaseCommand):
    help = "Generate favicon and touch icon files from a source logo image"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default="static/images/logo.png",
            help="Source logo image path (relative to project root)",
        )

    def handle(self, *args, **options):
        source = Path(options["input"])
        if not source.is_absolute():
            source = Path(settings.BASE_DIR) / source

        if not source.exists():
            raise CommandError(f"Logo file not found: {source}")

        output_dir = Path(settings.BASE_DIR) / "static" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)

        with Image.open(source).convert("RGBA") as image:
            image.save(output_dir / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])

            icon_32 = image.copy()
            icon_32.thumbnail((32, 32), Image.Resampling.LANCZOS)
            icon_32.save(output_dir / "favicon-32x32.png", format="PNG")

            icon_16 = image.copy()
            icon_16.thumbnail((16, 16), Image.Resampling.LANCZOS)
            icon_16.save(output_dir / "favicon-16x16.png", format="PNG")

            apple_icon = image.copy()
            apple_icon.thumbnail((180, 180), Image.Resampling.LANCZOS)
            apple_icon.save(output_dir / "apple-touch-icon.png", format="PNG")

        self.stdout.write(self.style.SUCCESS("✓ Generated favicon.ico, favicon-32x32.png, favicon-16x16.png, apple-touch-icon.png"))
