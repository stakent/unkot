import datetime

from django.test import TestCase
from django.utils import timezone

from unkot.users.models import User

from ..models import SearchIsap, SearchIsapResult, save_search_result


class SearchResultTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK'
        )
        self.user.save()
        self.addresses_3 = [f'deed { n }' for n in range(1, 4)]
        self.addresses_4 = [f'deed { n }' for n in range(1, 5)]

    def test_save_search_result_1(self):
        'Test saving search result without result change'
        query = 'test query'
        ts1_1 = timezone.now()
        save_search_result(query, addresses=self.addresses_3, user=self.user)
        ts1_2 = timezone.now()

        saved_search = SearchIsap.objects.get(query=query, user=self.user)

        saved_results = SearchIsapResult.objects.filter(search=saved_search)
        self.assertEqual(saved_results.count(), 1)
        saved_result = saved_results[0]
        self.assertListEqual(saved_result.result, self.addresses_3)
        self.assertAlmostEqual(
            saved_result.first_run_ts,
            saved_result.last_run_ts,
            delta=datetime.timedelta(milliseconds=10),
        )
        self.assertLess(ts1_1, saved_result.first_run_ts)
        self.assertGreater(ts1_2, saved_result.first_run_ts)
        self.assertLess(saved_result.first_run_ts, saved_result.last_run_ts)
        self.assertLess(ts1_1, saved_result.last_run_ts)
        self.assertGreater(ts1_2, saved_result.last_run_ts)

        first_run_ts = saved_result.first_run_ts
        ts2_1 = timezone.now()
        # save the same search result
        save_search_result(query, addresses=self.addresses_3, user=self.user)
        ts2_2 = timezone.now()

        saved_results = SearchIsapResult.objects.filter(search=saved_search)
        # still one result saved, because the result itself is the same
        # only last_run_ts timestamp was updated
        self.assertEqual(saved_results.count(), 1)
        saved_result = saved_results[0]
        self.assertListEqual(saved_result.result, self.addresses_3)

        self.assertEqual(first_run_ts, saved_result.first_run_ts)
        self.assertLess(ts2_1, saved_result.last_run_ts)
        self.assertGreater(ts2_2, saved_result.last_run_ts)

    def test_save_search_result_2(self):
        'Test saving search result with result change'
        query = 'test query'
        save_search_result(query, addresses=self.addresses_3, user=self.user)

        saved_search = SearchIsap.objects.get(query=query, user=self.user)

        saved_results = SearchIsapResult.objects.filter(search=saved_search)

        ts2_1 = timezone.now()
        save_search_result(query, addresses=self.addresses_4, user=self.user)
        ts2_2 = timezone.now()

        saved_results = SearchIsapResult.objects.filter(search=saved_search)
        self.assertEqual(saved_results.count(), 2)
        saved_result2 = saved_results[1]
        self.assertListEqual(saved_result2.result, self.addresses_4)

        self.assertLess(ts2_1, saved_result2.last_run_ts)
        self.assertGreater(ts2_2, saved_result2.last_run_ts)

    def test_save_search_first_run_ts_last_run_ts(self):
        'Test SaveSearch fields first_run_ts, last_run_ts'
        query = 'test query run_ts'
        save_search_result(query, addresses=self.addresses_3, user=self.user)
        saved_search = SearchIsap.objects.get(query=query, user=self.user)

        now = timezone.now()

        save_search_result(query, addresses=self.addresses_3, user=self.user, now=now)

        saved_results = SearchIsapResult.objects.filter(search=saved_search)
        saved_search = SearchIsap.objects.get(query=query, user=self.user)

        self.assertEqual(saved_search.first_run_ts, saved_results[0].first_run_ts)
        self.assertEqual(saved_search.last_run_ts, saved_results[0].last_run_ts)

        save_search_result(query, addresses=self.addresses_4, user=self.user)

        saved_results = SearchIsapResult.objects.filter(search=saved_search).order_by(
            '-last_run_ts'
        )
        saved_search = SearchIsap.objects.get(query=query, user=self.user)

        self.assertEqual(saved_search.first_run_ts, saved_results[1].first_run_ts)
        self.assertEqual(saved_search.last_run_ts, saved_results[0].last_run_ts)
