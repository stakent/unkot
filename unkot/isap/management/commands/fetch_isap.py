from django.core.management.base import BaseCommand
from isap.fetch_isap import fetch_isap


class Command(BaseCommand):
    help = "Fetches data from isap.sejm.gov.pl"

    def add_arguments(self, parser):
        parser.add_argument(
            "publisher",
            type=str,
            help="Publisher symbol: ALL, WDU, WMP, LDU, LMP, LDW. ALL means WDU and WMP",
        )
        parser.add_argument("year1", type=int, help="First year of time range")
        parser.add_argument("year2", type=int, help="Last year of time range")
        parser.add_argument(
            "--new_only",
            action="store_true",
            help="Fetch only new deeds",
        )

    def handle(self, *args, **options):
        n = fetch_isap(
            publisher=options["publisher"],
            year1=options["year1"],
            year2=options["year2"],
            new_only=options["new_only"],
        )
        self.stdout.write(self.style.SUCCESS(f"Fetched { n } deeds from ISAP"))
