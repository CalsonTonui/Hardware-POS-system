from django.shortcuts import render, redirect
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/index.html', {
        'products': products
    })

def product_add(request):
    return render(request, 'products/product_list.html')