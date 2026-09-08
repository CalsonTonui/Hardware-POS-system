from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils import timezone

from products.models import Product
from services.models import Service
from inventory.models import Inventory
from purchases.models import Purchase
from sales.models import Sale


def dashboard(request):

    # Today's date
    today = timezone.localdate()

    # =====================================================
    # BASIC COUNTS
    # =====================================================

    product_count = Product.objects.count()

    services_count = Service.objects.count()

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

    # =====================================================
    # TODAY'S SALES
    # =====================================================

    today_sales = Sale.objects.filter(
        sale_date__date=today
    )

    today_sales_total = today_sales.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Cash sales
    cash_sales = today_sales.filter(
        payment_method='Cash'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # M-Pesa sales
    mpesa_sales = today_sales.filter(
        payment_method='M-Pesa'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # =====================================================
    # TODAY'S PURCHASES
    # =====================================================

    today_purchases = Purchase.objects.filter(
        purchase_date__date=today
    )

    purchase_total_expression = ExpressionWrapper(
        F('quantity') * F('buying_price'),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2
        )
    )

    today_purchase_total = today_purchases.aggregate(
        total=Sum(purchase_total_expression)
    )['total'] or 0

    # =====================================================
    # TODAY'S SALES TABLE
    # =====================================================

    recent_sales = list(
        Sale.objects.select_related(
            'product'
        ).filter(
            sale_date__date=today
        ).order_by(
            'sale_date'
        )[:10]
    )

    # Calculate remaining stock after each sale
    sales_running_stock = {}

    for sale in recent_sales:

        product_id = sale.product_id

        # Get current stock
        inventory = Inventory.objects.filter(
            product_id=product_id
        ).first()

        current_stock = inventory.quantity if inventory else 0

        # Start with current stock plus all sales made today
        if product_id not in sales_running_stock:

            today_product_sales = Sale.objects.filter(
                product_id=product_id,
                sale_date__date=today
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0

            sales_running_stock[product_id] = (
                current_stock + today_product_sales
            )

    # Calculate remaining quantity for each sale
    for sale in recent_sales:

        product_id = sale.product_id

        sales_running_stock[product_id] -= sale.quantity

        sale.remaining_quantity = sales_running_stock[product_id]

    # Display newest sales first
    recent_sales.reverse()

    # =====================================================
    # STOCK ALERTS
    # =====================================================

    stock_alerts = Inventory.objects.select_related(
        'product'
    ).filter(
        quantity__lte=F('reorder_level')
    ).order_by(
        'quantity'
    )[:10]

    # =====================================================
    # RECENT PURCHASES
    # =====================================================

    recent_purchases = Purchase.objects.select_related(
        'supplier',
        'product'
    ).order_by(
        '-purchase_date'
    )[:5]

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # Basic counts
        'product_count': product_count,
        'services_count': services_count,
        'total_stock': total_stock,

        # Stock
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,

        # Sales
        'today_sales_total': today_sales_total,
        'cash_sales': cash_sales,
        'mpesa_sales': mpesa_sales,
        'recent_sales': recent_sales,

        # Purchases
        'today_purchase_total': today_purchase_total,
        'recent_purchases': recent_purchases,

        # Stock alerts
        'stock_alerts': stock_alerts,
    }

    return render(
        request,
        'dashboard/index.html',
        context
    )