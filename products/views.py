from django.contrib import messages
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, render, redirect

from .models import Product
from .forms import ProductForm
from inventory.models import Inventory
from accounts.activity import log_activity

# =========================================================
# PRODUCT LIST
# =========================================================

def product_list(request):

    search = request.GET.get('search', '').strip()

    products = Product.objects.all().order_by('name')

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(barcode__icontains=search) |
            Q(category__icontains=search)
        )

    # ---------- STATISTICS ----------
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
        'total_products': total_products,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }

    return render(request, 'products/index.html', context)


# =========================================================
# PRODUCT ADD
# =========================================================

def product_add(request):

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()

            # Create inventory record if one doesn't exist
            Inventory.objects.get_or_create(
                product=product,
                defaults={'quantity': 0}
            )

            messages.success(
                request,
                f"{product.name} added successfully."
            )
            log_activity(
                request,
                'product_added',
                f'Product added: {product.name}',
                target_type='Product',
                target_id=product.id,
            )
            return redirect('products')
    else:
        form = ProductForm()

    return render(request, 'products/add.html', {'form': form})


def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle image removal BEFORE form save
        remove_image = request.POST.get('remove_image') == 'on'
        new_image_uploaded = 'image' in request.FILES

        # Keep a reference to the old image file
        old_image = product.image if product.image else None

        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            product = form.save()

            # If user checked "remove image" OR uploaded a new image,
            # delete the old file from disk
            if old_image:
                if remove_image or new_image_uploaded:
                    # Don't delete if the file is being reused (same path)
                    if product.image and product.image.name == old_image.name:
                        pass  # Same file, don't delete
                    else:
                        try:
                            old_image.delete(save=False)
                        except Exception:
                            pass

            # If user wants no image, clear the field
            if remove_image:
                product.image = None
                product.save()

            messages.success(
                request,
                f"{product.name} updated successfully."
            )
            log_activity(
                request,
                'product_edited',
                f'Product edited: {product.name}',
                target_type='Product',
                target_id=product.id,
            )
            return redirect('products')
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'products/edit.html',
        {
            'form': form,
            'product': product,
        }
    )

# =========================================================
# PRODUCT DELETE
# =========================================================

def product_delete(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()

        messages.success(
            request,
            f"{product_name} deleted successfully."
        )
        log_activity(
            request,
            'product_deleted',
            f'Product deleted: {product_name}',
        )
        return redirect('products')

    return render(
        request,
        'products/delete.html',
        {'product': product}
    )