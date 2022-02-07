'simulate_running_search '
from datetime import datetime, timedelta

from django.utils import timezone

from unkot.isap.models import save_search_result
from unkot.users.models import User

from .filter_deeds import filter_deeds


def simulate_running_search(query, name, date_from, date_to, dt=timedelta(days=1)):
    '''
    Simulate performing search by user identified by an email.

    Parameters:
    query(str) filter terms
    name (str) name identifing the user
    date_from(str) date of the first search
    date_to(str) date of the last search
    dt(timdelta) optional interval between searches, default one day
    '''
    user = User.objects.get(name=name)
    ts1 = datetime.fromisoformat(date_from)
    ts1 = ts1.replace(tzinfo=timezone.get_default_timezone())
    ts2 = datetime.fromisoformat(date_to)
    ts2 = ts2.replace(tzinfo=timezone.get_default_timezone())
    now = ts1
    while now <= ts2:
        print(f'==== now: { now }')
        addresses = filter_deeds(query, now)
        save_search_result(query=query, addresses=addresses, user=user)
        now += dt
