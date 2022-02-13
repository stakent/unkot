"filter_deeds "
from collections import namedtuple

from django.contrib.postgres.search import SearchQuery

from unkot.isap.models import DeedText

from .check_deeds_list_ordering import check_deeds_list_ordering

DT = namedtuple('DT', ['address', 'change_date'])


def filter_deeds(filter_terms, now):
    """Filter deeds using provided filter terms.

    Parameters:
    filter_terms(str) filter terms
    now(datetime with timezone) set when filtering was done

    Returns:
    list of deeds addresses
    """
    # FIXME 'plain' or 'websearch' -> , search_type='websearch')
    query = SearchQuery(filter_terms, config="polish")
    # print(f'==== filter_deeds: query: { query }')
    dts = list(
        DeedText.objects.filter(search_vector=query, change_date__lte=now).values(
            "deed_id", "change_date"
        )
    )
    # FIXME line below is slow, make to work .order_by("change_date")?
    dts = sorted(dts, key=lambda dt: dt['deed_id'])
    dts = sorted(dts, key=lambda dt: dt['change_date'], reverse=True)

    dts2 = [DT(dt['deed_id'], dt['change_date']) for dt in dts]
    check_deeds_list_ordering(dts2)  # <<<< FIXME remove ^^^ in production

    addresses_all = [dt['deed_id'] for dt in dts]
    addresses = []
    for addr in addresses_all:
        if addr not in addresses:
            addresses.append(addr)
    return addresses
