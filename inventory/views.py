from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Inventory


def inventory_list(request):

    query = request.GET.get('q', '').strip()

    inventory = Inventory.objects.select_related(
        'product'
    ).order_by('product__name')

    if query:
        inventory = inventory.filter(
            Q(product__name__icontains=query) |
            Q(product__barcode__icontains=query) |
            Q(product__category__icontains=query)
        )

    paginator = Paginator(inventory, 10)

    page_number = request.GET.get('page')

    inventory_page = paginator.get_page(page_number)

    context = {
        'inventory': inventory_page,
        'query': query,
    }

    return render(
        request,
        'inventory/index.html',
        context
    )