import json
import csv
from datetime import timedelta
from accounts.activity import log_activity
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Sale
from inventory.models import Inventory
from products.models import Product
from accounts.models import User


# =========================================================
# ADMIN: ALL SALES HISTORY (read-only, with filters)
# =========================================================

@login_required
def sale_list(request):
    """Admin sales history — shows ALL sales with filters."""
    sales = Sale.objects.select_related('product', 'cashier').order_by('-sale_date')

    # Filters
    cashier_id = request.GET.get('cashier', '')
    payment = request.GET.get('payment', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '').strip()

    if cashier_id:
        sales = sales.filter(cashier_id=cashier_id)
    if payment:
        sales = sales.filter(payment_method=payment)
    if date_from:
        sales = sales.filter(sale_date__date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__date__lte=date_to)
    if search:
        sales = sales.filter(
            Q(product__name__icontains=search) |
            Q(mpesa_code__icontains=search)
        )

    # Summary
    total_sales = sales.aggregate(t=Sum('total_amount'))['t'] or 0
    total_count = sales.count()
    total_items = sales.aggregate(t=Sum('quantity'))['t'] or 0
    cash_total = sales.filter(payment_method='Cash').aggregate(t=Sum('total_amount'))['t'] or 0
    mpesa_total = sales.filter(payment_method='M-Pesa').aggregate(t=Sum('total_amount'))['t'] or 0

    # Cashiers for filter
    cashiers = User.objects.filter(
        role__in=['cashier', 'admin', 'manager']
    ).order_by('username')

    context = {
        'sales': sales[:200],
        'cashiers': cashiers,
        'total_sales': total_sales,
        'total_count': total_count,
        'total_items': total_items,
        'cash_total': cash_total,
        'mpesa_total': mpesa_total,
        'filter_cashier': cashier_id,
        'filter_payment': payment,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
        'filter_search': search,
    }
    return render(request, 'sales/sale_list.html', context)


# =========================================================
# CASHIER: MY SALES (only their own)
# =========================================================

@login_required
def my_sales(request):
    """Cashier's own sales history."""
    sales = Sale.objects.filter(
        cashier=request.user
    ).select_related('product').order_by('-sale_date')

    today = timezone.localdate()
    today_sales = sales.filter(sale_date__date=today)

    context = {
        'sales': sales[:200],
        'today_total': today_sales.aggregate(t=Sum('total_amount'))['t'] or 0,
        'today_count': today_sales.count(),
        'total_count': sales.count(),
        'total_items': sales.aggregate(t=Sum('quantity'))['t'] or 0,
    }
    return render(request, 'sales/my_sales.html', context)


# =========================================================
# POS TERMINAL (cashier screen)
# =========================================================

@login_required
def pos_terminal(request):
    """Cashier POS screen."""
    from django.db.models import Sum

    products = Product.objects.filter(
        inventory__quantity__gt=0
    ).order_by('name')

    # Top 8 best sellers (by quantity sold)
    top_products = Sale.objects.values(
        'product__id',
        'product__name',
        'product__selling_price'
    ).annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:8]

    # Fetch full product objects for the top ones
    top_ids = [p['product__id'] for p in top_products]
    top_product_objs = Product.objects.filter(
        id__in=top_ids,
        inventory__quantity__gt=0
    ).order_by('name')

    return render(request, 'sales/pos_terminal.html', {
        'products': products,
        'top_products': top_product_objs,
    })


# =========================================================
# CREATE SALE (called from POS via AJAX)
# =========================================================

@login_required
def create_sale(request):
    """Handle POS checkout: save sale, update inventory, return receipt."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'})

    payment_method = data.get('payment_method')
    amount_received = float(data.get('amount_received', 0))
    items = data.get('items', [])
    mpesa_code = data.get('mpesa_code', '') or None

    if not items:
        return JsonResponse({'success': False, 'error': 'Cart is empty.'})

    if payment_method not in ['Cash', 'M-Pesa']:
        return JsonResponse({'success': False, 'error': 'Invalid payment method.'})

    try:
        with transaction.atomic():
            total_amount = 0
            receipt_items = []
            last_sale = None

            for item in items:
                product = Product.objects.get(id=item['id'])
                qty = int(item['qty'])

                try:
                    inventory = Inventory.objects.get(product=product)
                except Inventory.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'No inventory record for {product.name}.'
                    })

                if qty > inventory.quantity:
                    return JsonResponse({
                        'success': False,
                        'error': f'Not enough stock for {product.name}. '
                                 f'Available: {inventory.quantity}'
                    })

                line_total = product.selling_price * qty
                total_amount += line_total

                sale = Sale.objects.create(
                    product=product,
                    cashier=request.user,
                    quantity=qty,
                    selling_price=product.selling_price,
                    total_amount=line_total,
                    payment_method=payment_method,
                    mpesa_code=mpesa_code,
                )
                last_sale = sale

                inventory.quantity -= qty
                inventory.save()

                receipt_items.append({
                    'name': product.name,
                    'qty': qty,
                    'price': float(product.selling_price),
                    'total': float(line_total),
                })

            change = amount_received - float(total_amount)
            receipt_number = f"RCP-{timezone.now().strftime('%Y%m%d')}-{last_sale.id}"

            # Log the sale
            log_activity(
                request,
                'sale_created',
                f'Sale completed: {len(receipt_items)} item(s), total KSh {total_amount:.2f}, '
                f'payment: {payment_method}',
                target_type='Sale',
                target_id=last_sale.id if last_sale else None,
            )

            return JsonResponse({
                'success': True,
                'receipt': {
                    'number': receipt_number,
                    'date': timezone.now().strftime('%d %b %Y, %H:%M'),
                    'cashier': request.user.get_full_name() or request.user.username,
                    'items': receipt_items,
                    'total': float(total_amount),
                    'received': amount_received,
                    'change': max(change, 0),
                    'payment_method': payment_method,
                    'mpesa_code': mpesa_code,
                }
            })

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# =========================================================
# EXPORT SALES TO CSV
# =========================================================

@login_required
def export_sales_csv(request):
    """Export filtered sales to CSV."""
    sales = Sale.objects.select_related('product', 'cashier').order_by('-sale_date')

    # Apply same filters as sale_list
    cashier_id = request.GET.get('cashier', '')
    payment = request.GET.get('payment', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '').strip()

    if cashier_id:
        sales = sales.filter(cashier_id=cashier_id)
    if payment:
        sales = sales.filter(payment_method=payment)
    if date_from:
        sales = sales.filter(sale_date__date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__date__lte=date_to)
    if search:
        sales = sales.filter(
            Q(product__name__icontains=search) |
            Q(mpesa_code__icontains=search)
        )

    response = HttpResponse(content_type='text/csv')
    filename = f"sales_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Time', 'Product', 'Category', 'Cashier',
        'Quantity', 'Unit Price', 'Total', 'Payment', 'M-Pesa Code'
    ])

    for sale in sales:
        writer.writerow([
            sale.sale_date.strftime('%Y-%m-%d'),
            sale.sale_date.strftime('%H:%M'),
            sale.product.name,
            getattr(sale.product, 'category', ''),
            sale.cashier.get_full_name() if sale.cashier else '—',
            sale.quantity,
            float(sale.selling_price),
            float(sale.total_amount),
            sale.payment_method,
            sale.mpesa_code or '',
        ])

    return response


# =========================================================
# SALE DETAIL
# =========================================================

@login_required
def sale_detail(request, sale_id):
    """Display details of a single sale."""
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sales/sale_detail.html', {'sale': sale})