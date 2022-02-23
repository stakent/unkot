'run_subscribed_searches '

from django.utils import timezone

from unkot.isap.models import SearchIsap, save_search_result

from .filter_deeds import filter_deeds


def run_subscribed_searches() -> None:
    '''Run searches subscribed by users.'''
    searches = SearchIsap.objects.filter(subscribed=True)
    for search in searches:
        now = timezone.now()
        addresses = filter_deeds(search.query, now)
        save_search_result(
            query=search.query, addresses=addresses, user=search.user, now=now
        )
