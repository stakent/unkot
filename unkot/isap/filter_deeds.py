"filter_deeds "
from django.contrib.postgres.search import SearchQuery

from .models import DeedText


def filter_deeds(filter_terms):
    """Filter deeds using provided filter terms.

    Parameters:
    filter_terms(str) filter terms

    Returns:
    list of deeds addresses
    """
    query = SearchQuery(filter_terms, config="polish")
    dts = (
        DeedText.objects.filter(search_vector=query)
        .values("deed_id", "change_date")
        .distinct("deed_id")
    )  # FIXME line below is slow, make to work .order_by("change_date")?
    addresses = [dt["deed_id"] for dt in sorted(dts, key=lambda dt: dt["change_date"])]
    return addresses
