from django.contrib import messages
from django.db.models import (Q, F)
from django.shortcuts import get_object_or_404, render, redirect

from .models import Product
from .forms import ProductForm
from inventory.models import Inventory


def product_list(request):

    search = request.GET.get('search', '').strip()

    products = Product.objects.all().order_by('name')

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(barcode__icontains=search) |
            Q(category__icontains=search)
        )

    # =====================================================
    # PRODUCT STATISTICS
    # =====================================================

    total_products = Product.objects.count()

    in_stock = Inventory.objects.filter(
        quantity__gt=0
    ).values('product').distinct().count()

    low_stock = Inventory.objects.filter(
        quantity__gt=0,
        quantity__lte=F('reorder_level')
    ).values('product').distinct().count()

    out_of_stock = Product.objects.filter(
        inventory__quantity=0
    ).distinct().count()

    context = {
        'products': products,
        'search': search,

        # Statistics
        'total_products': total_products,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }

    return render(
        request,
        'products/index.html',
        context
    )
def product_add(request):

    if request.method == 'POST':

        form = ProductForm(request.POST)

        if form.is_valid():

            product = form.save()

            # Create inventory record if one does not exist
            Inventory.objects.get_or_create(
                product=product,
                defaults={'quantity': 0}
            )

            messages.success(
                request,
                f"{product.name} added successfully."
            )

            return redirect('products')

    else:
        form = ProductForm()

    return render(
        request,
        'products/add.html',
        {'form': form}
    )


def product_edit(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                f"{product.name} updated successfully."
            )

            return redirect('products')

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        'products/edit.html',
        {
            'form': form,
            'product': product,
        }
    )


def product_delete(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        product_name = product.name

        product.delete()

        messages.success(
            request,
            f"{product_name} deleted successfully."
        )

        return redirect('products')

    return render(
        request,
        'products/delete.html',
        {
            'product': product,
        }
    )