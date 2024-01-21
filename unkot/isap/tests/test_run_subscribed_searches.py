from django.core import mail
from django.test import TestCase

from unkot.users.models import User

from ..models import SearchIsap
from ..run_subscribed_searches import run_subscribed_searches


class RunSubscribedSearchesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser12',
            password='1X<ISRUkw+tuK123',
            email='test12@example.com',
        )
        self.user.save()
        self.addresses_3 = [f'deed { n }' for n in range(1, 4)]
        self.addresses_4 = [f'deed { n }' for n in range(1, 5)]

    def test_run_subscribed_searches_user_search_not_subscribed(self):
        'Test run_subscribed_searches returning new result for not subscribed search.'
        query = 'random query for notification testing 12'

        ss, _ = SearchIsap.objects.get_or_create(query=query, user=self.user)
        ss.subscribed = False
        ss.save()

        self.assertEqual(len(mail.outbox), 0)

        run_subscribed_searches()

        self.assertEqual(len(mail.outbox), 0)

    def test_run_subscribed_searches_user_search_subscribed(self):
        'Test run_subscribed_searches returning new result for subscribed search.'
        query = 'random query for notification testing 13'

        ss, _ = SearchIsap.objects.get_or_create(query=query, user=self.user)
        ss.subscribed = True
        ss.save()

        self.assertEqual(len(mail.outbox), 0)

        run_subscribed_searches()

        self.assertEqual(len(mail.outbox), 1)
