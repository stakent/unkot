import logging

from django.core.management.base import BaseCommand
from isap.extract_text_from_deeds import extract_text_from_deeds

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetches data from isap.sejm.gov.pl"

    # def add_arguments(self, parser):
    #   parser.add_argument('titles', nargs='+', type=str)

    def handle(self, *args, **options):
        n = extract_text_from_deeds(log)
        self.stdout.write(self.style.SUCCESS(f"Extracted text from { n } deeds"))
