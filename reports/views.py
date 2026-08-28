
from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils import timezone

from sales.models import Sale
from purchases.models import Purchase
from inventory.models import Inventory


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
