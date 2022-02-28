from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set verified bit for an email account"

    def add_arguments(self, parser):
        parser.add_argument("address", type=str, help='email address')
        parser.add_argument("value", help='value for "verified" bit: 0 or 1')

    def handle(self, *args, **options):
        address = options["address"]
        value = options["value"]
        email = EmailAddress.objects.get(email=address)
        value = int(value)
        email.verified = value != 0
        email.save()
