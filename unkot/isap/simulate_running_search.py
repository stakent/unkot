'simulate_running_search '
from collections import namedtuple
from datetime import datetime, timedelta

from django.utils import timezone

from unkot.isap.models import save_search_result
from unkot.users.models import User

from .filter_deeds import filter_deeds

SR = namedtuple('SR', ['ts', 'addresses'])


def check_search_results(query=None, new_res=None, prev_res=None):
    if len(new_res.addresses) < len(prev_res.addresses):
        msg = 'new result has fewer documents than, previous one '
        msg += f'n_sr.ts: { new_res.ts } { len(new_res.addresses) } '
        msg += f'p_sr.ts: { prev_res.ts } { len(prev_res.addresses) } '
        raise ValueError(msg)
    for addr in prev_res.addresses:
        msg = 'new result: mising address present in previous result '
        msg += f'new result ts: { new_res.ts }, missing address: { addr }'
        raise ValueError(msg)
        if addr not in new_res.addresses:
            raise ValueError(msg)


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
    prev_res = None
    now = ts1
    while now <= ts2:
        print(f'==== now: { now }')
        addresses = filter_deeds(query, now)
        new_res = SR(now, addresses)
        if prev_res is not None:
            check_search_results(query=query, new_res=new_res, prev_res=prev_res)
        save_search_result(query=query, addresses=addresses, user=user, now=now)
        now += dt
