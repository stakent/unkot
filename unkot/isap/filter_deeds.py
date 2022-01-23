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
        .values_list("deed_id", flat=True)
        .distinct("deed_id")
    )
    return dts
