import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import F, Func
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .check_deeds_list_ordering import check_deeds_list_ordering
from .filter_deeds import filter_deeds
from .models import (
    Deed,
    SearchIsap,
    SearchIsapResult,
    load_deed_text,
    save_search_result,
    send_new_isap_search_result_email,
)


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
        addresses = filter_deeds(query, timezone.now())
        deeds_count_query = len(addresses)
        paginator = Paginator(addresses, 10)

        if request.user.is_authenticated and 'save search button' in request.POST:
            save_search_result(query, addresses, request.user, timezone.now())
    else:
        addresses = Deed.objects.order_by("-change_date", 'address').values("address")
        paginator = Paginator(addresses, 10)

    deeds_count_all = Deed.objects.count()

    page_obj = paginator.get_page(page_number)
    deeds = list(
        Deed.objects.filter(address__in=page_obj.object_list).order_by(
            '-change_date', 'address'
        )
    )
    pages_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    if request.user.is_authenticated:
        saved_searches_count = SearchIsap.objects.filter(user=request.user).count()
    else:
        saved_searches_count = 0

    check_deeds_list_ordering(deeds)

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
    searches = SearchIsap.objects.filter(user=request.user).order_by('-last_run_ts')
    # FIXME use annotation on reverse one-to-many relation in previous line
    for n in range(0, len(searches)):
        count = SearchIsapResult.objects.filter(search=searches[n]).count()
        searches[n].count = count
    context = {
        'searches': searches,
    }
    return render(request, "isap/saved_searches_list.html", context)


@login_required
def saved_search_delete(request, id):
    try:
        search = SearchIsap.objects.get(id=id)
    except SearchIsap.DoesNotExist:
        return redirect('saved_isap_searches')
    if request.method == 'POST':
        if 'delete button' in request.POST:
            search.delete()
        return redirect('saved_isap_searches')
    context = {'search': search}
    return render(request, "isap/saved_search_delete.html", context)


@login_required
def search_isap_detail(request, id):
    search = SearchIsap.objects.get(id=id)
    if request.method == 'POST':
        search.subscribed = 'yes' in request.POST['subscribe-search']
        search.save()
    results = (
        SearchIsapResult.objects.filter(search=search)
        .annotate(number_of_results=Func(F('result'), function='CARDINALITY'))
        .order_by('-last_run_ts')
    )
    last_run_ts = datetime.datetime(1, 1, 1, 0, 0, tzinfo=datetime.UTC)
    for i in range(0, len(results)):
        # FIXME search.last_run_ts has incorrect value
        last_run_ts = max(last_run_ts, results[i].last_run_ts)
        new_result = results[i]
        try:
            previous_result = results[i + 1]
        except IndexError:
            continue
        new_result_docs = set(new_result.result)
        previous_result_docs = set(previous_result.result)
        # WDU20200001325
        # 01234567890123
        new_docs = list(new_result_docs - previous_result_docs)
        new_deeds = Deed.objects.filter(address__in=new_docs).order_by(
            '-change_date', 'address'
        )
        removed_docs = list(previous_result_docs - new_result_docs)
        removed_deeds = Deed.objects.filter(address__in=removed_docs).order_by(
            '-change_date', 'address'
        )
        results[i].new_deeds = new_deeds
        results[i].removed_deeds = removed_deeds
    context = {
        'search': search,
        'last_run_ts': last_run_ts,
        'results': results,
    }
    return render(request, "isap/saved_search_detail.html", context)


@login_required
def search_isap_result_detail(request, id):
    page_number = request.GET.get('page', 1)
    result = SearchIsapResult.objects.get(id=id)
    result_docs_count = len(result.result)
    paginator = Paginator(result.result, 10)
    page_obj = paginator.get_page(page_number)
    deeds = Deed.objects.filter(address__in=page_obj.object_list).order_by(
        '-change_date', 'address'
    )
    pages_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    context = {
        'deeds': deeds,
        'result': result,
        'result_docs_count': result_docs_count,
        "page_obj": page_obj,
        "pages_range": pages_range,
    }
    return render(request, "isap/saved_search_result_detail.html", context)


@user_passes_test(lambda user: user.is_staff)
def send_new_isap_search_result_email_view(request, id):
    if request.method == 'GET':
        return Http404
    ssr = SearchIsapResult.objects.get(id=id)
    send_new_isap_search_result_email(ssr)
    return HttpResponse('Wiadomość wysłana - przeładuj stronę')
