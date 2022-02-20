from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from unkot.users.models import User

from ..models import (
    SearchIsap,
    SearchIsapResult,
    save_search_result,
    send_new_isap_search_result_email,
)


class SearchResultEmailTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser2',
            password='1X<ISRUkw+tuK123',
            email='test3@example.com',
        )
        self.user.save()
        self.addresses_3 = [f'deed { n }' for n in range(1, 4)]
        self.addresses_4 = [f'deed { n }' for n in range(1, 5)]

    def test_search_new_result_not_subscribed(self):
        'Test sending email notification for search not subsciribed by user'
        query = 'random query for notification testing 1'
        now = timezone.now()

        # test subscribed True, False
        save_search_result(query, addresses=self.addresses_3, user=self.user, now=now)
        self.assertEqual(len(mail.outbox), 0)

    def test_search_new_result_subscribed(self):
        'Test sending email notification for search subscribed by user'
        query = 'random query for notification testing 2'
        now = timezone.now()

        ss, _ = SearchIsap.objects.get_or_create(query=query, user=self.user)
        ss.subscribed = True
        ss.save()
        save_search_result(query, addresses=self.addresses_3, user=self.user, now=now)

        self.assertEqual(len(mail.outbox), 1)

    def test_search_new_result_email_content(self):
        'Test sending email content'
        query = 'random query for notification testing email content'
        now = timezone.now()
        result = ['addr1', 'addr2', 'addr3']

        ss, _ = SearchIsap.objects.get_or_create(query=query, user=self.user)
        ss.save()
        ssr, _ = SearchIsapResult.objects.get_or_create(
            search=ss,
            first_run_ts=now,
            last_run_ts=now,
            result=result,
        )
        ssr.save()

        send_new_isap_search_result_email(ssr)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(self.user.email in email.to)

        # query
        self.assertTrue(query in email.subject)
        self.assertTrue(query in email.body)
        self.assertTrue(query in email.message().as_string())

        # result_url
        ssr = SearchIsapResult.objects.get(last_run_ts=now)
        result_url = reverse('search_isap_result_detail', kwargs={'id': ssr.id})
        self.assertIn(f'https://unkot.pl{ result_url }', email.body)
        self.assertIn(
            f'<a href="https://unkot.pl{ result_url }">', email.message().as_string()
        )

        # search_url
        search_url = reverse('search_isap_detail', kwargs={'id': ss.id})
        self.assertIn(f'https://unkot.pl{ search_url }', email.body)
        self.assertIn(
            f'<a href="https://unkot.pl{ search_url }">', email.message().as_string()
        )

        # treść text
        # treść html
        # linki: new_docs: link to ISAP meta page
        # unsubsciribe text
        # unsubscribe link
        # self.assertTrue(
        #    f'<a href="{ user_profile_url }">' in email.message().as_string()
        # )

        # test sending one email for given result, query and user
