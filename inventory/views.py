from django.shortcuts import render
from .models import Inventory
from django.db.models import Q
from django.core.paginator import Paginator

def inventory_list(request):
    query = request.GET.get('q')

    inventory = Inventory.objects.select_related('product')

    if query:
        inventory = inventory.filter(
            Q(product__name__icontains=query) |
            Q(product__barcode__icontains=query)
        )
    paginator = Paginator(inventory, 10)

    page_number = request.GET.get('page')

    inventory = paginator.get_page(page_number)

    context = {
        'inventory': inventory,
        'query': query,
    }

    return render(request, 'inventory/index.html', context)