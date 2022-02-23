from django.core.management.base import BaseCommand

from ...run_subscribed_searches import run_subscribed_searches


class Command(BaseCommand):
    help = 'Run searches subsribed by users.'

    def handle(self, *args, **options):
        run_subscribed_searches()
        self.stdout.write(self.style.SUCCESS("Running subscribed searches done."))
