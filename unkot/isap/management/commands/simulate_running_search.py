from django.core.management.base import BaseCommand
from ...simulate_running_search import simulate_running_search


class Command(BaseCommand):
    help = 'Simulate running a search.'

    def add_arguments(self, parser):
        parser.add_argument(
            'query', type=str, help='filter terms enclosed in a pair of "\'"'
        )
        parser.add_argument('name', type=str, help='name address of the user')
        parser.add_argument('date_from', type=str, help='first day of the simulation')
        parser.add_argument('date_to', type=str, help='first day of the simulation')

    def handle(self, *args, **options):
        simulate_running_search(
            query=options['query'],
            name=options['name'],
            date_from=options['date_from'],
            date_to=options['date_to'],
        )
        self.stdout.write(self.style.SUCCESS("Simulation done."))
