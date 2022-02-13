from datetime import datetime, timedelta
import random

from django.test import TestCase
from django.utils import timezone

from ..filter_deeds import filter_deeds
from ..models import Deed, DeedText, save_deed_text
from ..check_deeds_list_ordering import check_deeds_list_ordering


class DeedsOrderingTestCase(TestCase):
    def setUp(self):
        self.tz = timezone.get_default_timezone()
        self.future_date = datetime(9999, 1, 1, tzinfo=self.tz)
        random.seed(1)
        number_of_deeds = 123
        start_day = datetime(1970, 1, 2, tzinfo=self.tz)
        one_day = timedelta(days=1)
        for n in range(1, number_of_deeds + 1):
            addr = f'deed { n }'
            change_date = start_day + n * one_day
            text = f'text for deed { n }'
            deed = Deed(address=addr, change_date=change_date)
            deed.save()
            save_deed_text(deed.address, change_date, text)

    def test_filter_deeds_order_empty_result(self):
        query = 'empty test query'
        addresses = filter_deeds(query, self.future_date)
        self.assertEqual(len(addresses), 0)

    def test_filter_deeds_order_all_deeds(self):
        query = 'for deed'
        addresses = filter_deeds(query, self.future_date)
        self.assertEqual(len(addresses), 123)
        deeds = []
        for addr in addresses:
            deed = Deed.objects.get(address=addr)
            deeds.append(deed)
            #  self.assertEqual(self.check_deeds_list(deeds), '')

    def test_check_deed_list_ordering(self):
        d1 = Deed(
            address='deed 1',
            change_date=datetime(2000, 1, 10, tzinfo=self.tz),
            title='deed 1',
        )
        d2 = Deed(
            address='deed 2',
            change_date=datetime(2000, 1, 11, tzinfo=self.tz),
            title='deed 2',
        )
        d3 = Deed(
            address='deed 3',
            change_date=datetime(2000, 1, 12, tzinfo=self.tz),
            title='deed 3',
        )

        d1a = Deed(
            address='deed 1a',
            change_date=datetime(2000, 1, 10, tzinfo=self.tz),
            title='deed 1a',
        )
        d1b = Deed(
            address='deed 1b',
            change_date=datetime(2000, 1, 10, tzinfo=self.tz),
            title='deed 1b',
        )

        deeds_ok = [
            [],
            [d1],
            [d1, d1],  # ok: address and change_date are the same in both deeds
            [d3, d2, d1],  # ok: order_by('-change_date')
            [d1a, d1b],  # ok: change_date equal, wrong ored by address
        ]
        for deeds in deeds_ok:
            try:
                check_deeds_list_ordering(deeds)
            except ValueError:
                self.fail(
                    f'check_deeds_list raised ValueError unexpectedly for "{ deeds }"'
                )

        deeds_not_ok = [
            [d1, d2, d3],  # not ok: oldest deed first, youngest last
            [d1b, d1a],  # not ok: change_date equal, wrong ored by address
        ]
        for deeds in deeds_not_ok:
            with self.assertRaises(ValueError):
                check_deeds_list_ordering(deeds)
