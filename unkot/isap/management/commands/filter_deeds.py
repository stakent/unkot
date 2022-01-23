from django.core.management.base import BaseCommand
from isap.filter_deeds import filter_deeds


class Command(BaseCommand):
    help = "Filters deeds and optionaly dispalys them."

    def add_arguments(self, parser):
        parser.add_argument(
            "filter_terms", type=str, help='filter terms enclosed in a pair of "\'"'
        )

    def handle(self, *args, **options):
        deeds = filter_deeds(options["filter_terms"])
        self.stdout.write(self.style.SUCCESS(f"Returned { len(deeds) } deeds"))
