from django.shortcuts import render
from products.models import Product
from customers.models import Customer
from inventory.models import Inventory

def dashboard(request):
    context = {
        'product_count': Product.objects.count(),
        'customer_count': Customer.objects.count(),
        'inventory_count': Inventory.objects.count(),
    }

    return render(request, 'dashboard/index.html', context)