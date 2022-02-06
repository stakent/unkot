import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Func
from django.http import Http404
from django.shortcuts import render

from .filter_deeds import filter_deeds
from .models import Deed, SearchIsap, SearchIsapResult, load_deed_text


def deeds_list(request):
    "deeds_list"
    page_number = request.GET.get('page', request.POST.get('page', 1))

    if 'search button' in request.POST:
        query = request.POST.get('query')
    elif 'save search button' in request.POST:
        query = request.POST.get('query')
    elif 'query' in request.GET:
        query = request.GET['query']
    else:
        query = ''
    query = query.strip()
    deeds_count_query = None
    if query:
        addresses = filter_deeds(query)
        deeds_count_query = len(addresses)
        paginator = Paginator(addresses, 25)

        if request.user.is_authenticated and 'save search button' in request.POST:
            ss, created = SearchIsap.objects.get_or_create(
                query=query,
                user=request.user,
            )
            sr, _ = SearchIsapResult.objects.get_or_create(search=ss)
            sr.result = addresses
            sr.save()
            ss.save()
            count = SearchIsapResult.objects.filter(search=ss).count()
            print(
                f'==== save_search: { query } { sr.first_run_ts } { sr.last_run_ts } { count }'
            )
    else:
        addresses = Deed.objects.all().order_by("-change_date").values("address")
        paginator = Paginator(addresses, 25)

    deeds_count_all = Deed.objects.count()

    page_obj = paginator.get_page(page_number)
    deeds = Deed.objects.filter(address__in=page_obj.object_list)
    pages_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    if request.user.is_authenticated:
        saved_searches_count = SearchIsap.objects.filter(user=request.user).count()
    else:
        saved_searches_count = 0

    context = {
        "deeds_count_all": deeds_count_all,
        "deeds_count_query": deeds_count_query,
        "deeds": deeds,
        "page_obj": page_obj,
        "pages_range": pages_range,
        "query": query,
        "saved_searches_count": saved_searches_count,
    }
    return render(request, "isap/deeds_list.html", context)


def deed_detail(request, deed_address):
    "deed_detail"
    try:
        deed = Deed.objects.get(address=deed_address)
    except Deed.DoesNotExist:
        raise Http404("Deed does not exist")

    deed_text = load_deed_text(deed.address)

    context = {
        "deed": deed,
        "deed_text": deed_text,
    }
    return render(request, "isap/deed_detail.html", context)


@login_required
def saved_searches(request):
    searches = SearchIsap.objects.filter(user=request.user)
    # FIXME use annotation on reverse one-to-many relation in previous line
    for n in range(0, len(searches)):
        count = SearchIsapResult.objects.filter(search=searches[n]).count()
        searches[n].count = count
    context = {
        'searches': searches,
    }
    return render(request, "isap/saved_searches_list.html", context)


@login_required
def search_isap_detail(request, id):
    search = SearchIsap.objects.get(id=id)
    results = SearchIsapResult.objects.filter(search=search).annotate(
        number_of_results=Func(F('result'), function='CARDINALITY')
    )
    first_run_ts = datetime.datetime(9999, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    last_run_ts = datetime.datetime(1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    for sr in results:
        first_run_ts = min(first_run_ts, sr.first_run_ts)
        last_run_ts = max(last_run_ts, sr.last_run_ts)
    context = {
        'search': search,
        'first_run_ts': first_run_ts,
        'last_run_ts': last_run_ts,
        'results': results,
    }
    return render(request, "isap/saved_search_detail.html", context)
