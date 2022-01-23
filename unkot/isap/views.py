from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from .filter_deeds import filter_deeds
from .models import Deed, load_deed_text


def deeds_list(request):
    "deeds_list"
    query = request.GET.get("query")
    # print(f'===== query "{ query }"')

    deeds_count_query = None
    page_number = request.GET.get("page")
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
    context = {
        "deeds_count_all": deeds_count_all,
        "deeds_count_query": deeds_count_query,
        "deeds": deeds,
        "page_obj": page_obj,
        "pages_range": pages_range,
        "query": query,
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
