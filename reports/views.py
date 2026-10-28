from datetime import timedelta, date

from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Count
from django.utils import timezone
from decimal import Decimal
from sales.models import Sale
from purchases.models import Purchase
from inventory.models import Inventory
from products.models import Product

def reports_dashboard(request):

    today = timezone.localdate()

    # ==============================
    # TODAY'S SALES
    # ==============================

    today_sales = Sale.objects.filter(
        sale_date__date=today
    )

    today_sales_total = today_sales.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    today_sales_count = today_sales.count()


    # ==============================
    # TODAY'S PURCHASES
    # ==============================

    today_purchases = Purchase.objects.filter(
        purchase_date__date=today
    )

    purchase_expression = ExpressionWrapper(
        F('quantity') * F('buying_price'),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2
        )
    )

    today_purchase_total = today_purchases.aggregate(
        total=Sum(purchase_expression)
    )['total'] or 0

    today_purchase_count = today_purchases.count()


    # ==============================
    # PAYMENT METHODS
    # ==============================

    cash_total = today_sales.filter(
        payment_method='Cash'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    mpesa_total = today_sales.filter(
        payment_method='M-Pesa'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0


    # ==============================
    # INVENTORY
    # ==============================

    total_stock = Inventory.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    low_stock_count = Inventory.objects.filter(
        quantity__gt=0,
        quantity__lte=F('reorder_level')
    ).count()

    out_of_stock_count = Inventory.objects.filter(
        quantity=0
    ).count()


    # ==============================
    # RECENT SALES
    # ==============================

    recent_sales = Sale.objects.select_related(
        'product'
    ).order_by(
        '-sale_date'
    )[:10]


    # ==============================
    # CONTEXT
    # ==============================

    context = {

        'today': today,

        'today_sales_total': today_sales_total,
        'today_sales_count': today_sales_count,

        'today_purchase_total': today_purchase_total,
        'today_purchase_count': today_purchase_count,

        'cash_total': cash_total,
        'mpesa_total': mpesa_total,

        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,

        'recent_sales': recent_sales,
    }


    return render(
        request,
        'reports/reports_dashboard.html',
        context
    )

def mpesa_report(request):
    """M-Pesa sales report for admins."""
    today = timezone.localdate()
    start_of_month = today.replace(day=1)
    last_30_days = today - timedelta(days=30)

    all_sales = Sale.objects.filter(payment_method='M-Pesa')

    today_sales = all_sales.filter(sale_date__date=today)
    month_sales = all_sales.filter(sale_date__date__gte=start_of_month)
    last30_sales = all_sales.filter(sale_date__date__gte=last_30_days)

    context = {
        'today_total': today_sales.aggregate(t=Sum('total_amount'))['t'] or 0,
        'today_count': today_sales.count(),

        'month_total': month_sales.aggregate(t=Sum('total_amount'))['t'] or 0,
        'month_count': month_sales.count(),

        'last30_total': last30_sales.aggregate(t=Sum('total_amount'))['t'] or 0,
        'last30_count': last30_sales.count(),

        'recent_mpesa_sales': all_sales.select_related('product').order_by('-sale_date')[:50],
        'today': today,
    }

    return render(request, 'reports/mpesa_report.html', context)


@login_required
def sales_by_cashier(request):
    """Report: total sales per cashier for a date range."""
    today = timezone.localdate()

    # Default: this month
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')

    if date_from_str:
        try:
            date_from = date.fromisoformat(date_from_str)
        except ValueError:
            date_from = today.replace(day=1)
    else:
        date_from = today.replace(day=1)

    if date_to_str:
        try:
            date_to = date.fromisoformat(date_to_str)
        except ValueError:
            date_to = today
    else:
        date_to = today

    # Get all cashiers
    cashiers = User.objects.filter(
        role__in=['cashier', 'admin', 'manager']
    ).order_by('username')

    report_data = []
    grand_total = 0
    grand_count = 0

    for cashier in cashiers:
        cashier_sales = Sale.objects.filter(
            cashier=cashier,
            sale_date__date__gte=date_from,
            sale_date__date__lte=date_to,
        )

        total = cashier_sales.aggregate(t=Sum('total_amount'))['t'] or 0
        count = cashier_sales.count()
        cash_total = cashier_sales.filter(payment_method='Cash').aggregate(
            t=Sum('total_amount')
        )['t'] or 0
        mpesa_total = cashier_sales.filter(payment_method='M-Pesa').aggregate(
            t=Sum('total_amount')
        )['t'] or 0

        report_data.append({
            'cashier': cashier,
            'total': total,
            'count': count,
            'cash_total': cash_total,
            'mpesa_total': mpesa_total,
        })

        grand_total += total
        grand_count += count

    # Sort by total sales descending
    report_data.sort(key=lambda x: x['total'], reverse=True)

    context = {
        'report_data': report_data,
        'grand_total': grand_total,
        'grand_count': grand_count,
        'date_from': date_from,
        'date_to': date_to,
        'today': today,
    }
    return render(request, 'reports/sales_by_cashier.html', context)

@login_required
def period_report(request):
    """Daily / Weekly / Monthly summary report."""
    period = request.GET.get('period', 'daily')
    today = timezone.localdate()

    if period == 'weekly':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == 'monthly':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:  # daily
        start = today
        end = today

    sales = Sale.objects.filter(
        sale_date__date__gte=start,
        sale_date__date__lte=end,
    ).select_related('product', 'cashier')

    total_sales = sales.aggregate(t=Sum('total_amount'))['t'] or 0
    total_count = sales.count()
    cash_total = sales.filter(payment_method='Cash').aggregate(t=Sum('total_amount'))['t'] or 0
    mpesa_total = sales.filter(payment_method='M-Pesa').aggregate(t=Sum('total_amount'))['t'] or 0

    # Top selling products
    top_products = sales.values('product__name').annotate(
        qty=Sum('quantity'),
        total=Sum('total_amount')
    ).order_by('-qty')[:10]

    context = {
        'period': period,
        'start': start,
        'end': end,
        'total_sales': total_sales,
        'total_count': total_count,
        'cash_total': cash_total,
        'mpesa_total': mpesa_total,
        'top_products': top_products,
        'sales': sales[:100],
    }
    return render(request, 'reports/period_report.html', context)

@login_required
def product_performance(request):
    """Product performance report."""
    today = timezone.localdate()
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')

    if date_from_str:
        try:
            date_from = date.fromisoformat(date_from_str)
        except ValueError:
            date_from = today - timedelta(days=30)
    else:
        date_from = today - timedelta(days=30)

    if date_to_str:
        try:
            date_to = date.fromisoformat(date_to_str)
        except ValueError:
            date_to = today
    else:
        date_to = today

    sales = Sale.objects.filter(
        sale_date__date__gte=date_from,
        sale_date__date__lte=date_to,
    )

    # Product performance
    performance = sales.values(
        'product__id',
        'product__name',
        'product__category',
    ).annotate(
        qty_sold=Sum('quantity'),
        total_revenue=Sum('total_amount'),
        transactions=Count('id'),
    ).order_by('-total_revenue')

    # All products
    all_products = Product.objects.all()

    # Products with no sales
    sold_product_ids = [p['product__id'] for p in performance]
    dead_products = all_products.exclude(id__in=sold_product_ids)[:10]

    context = {
        'performance': performance,
        'dead_products': dead_products,
        'date_from': date_from,
        'date_to': date_to,
        'today': today,
        'total_products': all_products.count(),
    }
    return render(request, 'reports/product_performance.html', context)