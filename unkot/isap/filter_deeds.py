"filter_deeds "
from datetime import datetime

from django.contrib.postgres.search import SearchQuery

from unkot.isap.models import DeedText


def filter_deeds(filter_terms: str, now: datetime) -> list[str | None]:
    """Filter deeds using provided filter terms.

    Parameters:
    filter_terms(str) filter terms
    now(datetime with timezone) set when filtering was done

    Returns:
        list of deed_id for matching deeds
    """

    query = SearchQuery(filter_terms, config='polish', search_type='websearch')
    dts = list(
        DeedText.objects.filter(
            search_vector=query, change_date__lte=now, seq=1
        ).values("deed_id", "change_date")
    )
    dts = sorted(dts, key=lambda dt: dt['deed_id'])  # type: ignore
    dts = sorted(dts, key=lambda dt: dt['change_date'], reverse=True)  # type: ignore
    addresses = [dt['deed_id'] for dt in dts]
    return addresses
