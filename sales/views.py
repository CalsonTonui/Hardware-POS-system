from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone

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


            # Get actual selling price
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



    # =====================================================
    # ALL SALES
    # =====================================================

    sales = Sale.objects.select_related(
        'product'
    ).order_by('-sale_date')



    # =====================================================
    # TODAY'S SALES
    # =====================================================

    today = timezone.localdate()

    today_sales = sales.filter(
        sale_date__date=today
    )


    today_total_sales = today_sales.aggregate(
        total=Sum('total_amount')
    )['total'] or 0



    # =====================================================
    # TOTAL TRANSACTIONS
    # =====================================================

    total_transactions = sales.count()



    # =====================================================
    # TOTAL ITEMS SOLD
    # =====================================================

    total_items_sold = sales.aggregate(
        total=Sum('quantity')
    )['total'] or 0



    # =====================================================
    # TOP 3 MOST SOLD PRODUCTS THIS YEAR
    # =====================================================

    current_year = today.year

    most_sold_items = Sale.objects.filter(
        sale_date__year=current_year
    ).values(
        'product__name',
        'product__unit'
    ).annotate(
        transaction_count=Count('id')
    ).order_by(
        '-transaction_count'
    )[:3]



    context = {

        'form': form,

        'sales': sales,

        'today_total_sales': today_total_sales,

        'total_transactions': total_transactions,

        'total_items_sold': total_items_sold,

        'most_sold_items': most_sold_items,

    }


    return render(
        request,
        'sales/sale_list.html',
        context
    )