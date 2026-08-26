from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import SaleForm
from .models import Sale
from inventory.models import Inventory


def sale_list(request):

    if request.method == 'POST':

        form = SaleForm(request.POST)

        if form.is_valid():

            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            try:
                inventory = Inventory.objects.get(product=product)
            except Inventory.DoesNotExist:
                messages.error(
                    request,
                    "This product does not have an inventory record."
                )
                return redirect('sale_list')

            if quantity > inventory.quantity:
                messages.error(
                    request,
                    f"Insufficient stock. Available quantity: {inventory.quantity}"
                )
                return redirect('sale_list')

            # Get the actual selling price from the product
            selling_price = product.selling_price

            # Calculate total
            total_amount = quantity * selling_price

            with transaction.atomic():

                sale = form.save(commit=False)

                sale.selling_price = selling_price
                sale.total_amount = total_amount

                sale.save()

                # Reduce inventory
                inventory.quantity -= quantity
                inventory.save()

            messages.success(
                request,
                "Sale completed successfully and inventory updated."
            )

            return redirect('sale_list')

    else:
        form = SaleForm()

    sales = Sale.objects.select_related(
        'product'
    ).order_by('-sale_date')

    context = {
        'form': form,
        'sales': sales,
    }

    return render(
        request,
        'sales/sale_list.html',
        context
    )