from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from .filter_deeds import filter_deeds
from .models import Deed, SearchIsap, load_deed_text


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
    else:
        addresses = Deed.objects.all().order_by("-change_date").values("address")
        paginator = Paginator(addresses, 25)

    deeds_count_all = Deed.objects.count()

    page_obj = paginator.get_page(page_number)
    deeds = Deed.objects.filter(address__in=page_obj.object_list)
    pages_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    if request.user.is_authenticated and 'save search button' in request.POST:
        ss, created = SearchIsap.objects.get_or_create(
            query=query,
            user=request.user,
        )
        if created:
            ss.first_run_ts = timezone.now()
        ss.last_run_ts = timezone.now()
        ss.result = addresses
        ss.save()

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
