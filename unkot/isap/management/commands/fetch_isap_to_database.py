from django.core.management.base import BaseCommand
from ...fetch_isap_to_database import fetch_isap_to_database


class Command(BaseCommand):
    help = "Fetches data from isap.sejm.gov.pl and stores text in database."

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
        n = fetch_isap_to_database(
            publisher=options["publisher"],
            year1=options["year1"],
            year2=options["year2"],
            new_only=options["new_only"],
        )
        self.stdout.write(self.style.SUCCESS(f"Fetched { n } deeds from ISAP"))
