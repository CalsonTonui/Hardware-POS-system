from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from accounts.activity import log_activity
from .models import Purchase
from .forms import PurchaseForm
from inventory.models import Inventory


def purchase_list(request):
    """Purchases list + form. Supports pre-selecting a product via ?product=ID."""

    # Read preselected product ID (for restock quick-action)
    preselected_product_id = request.GET.get('product', '')

    if request.method == "POST":
        form = PurchaseForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                purchase = form.save()

                inventory, created = Inventory.objects.get_or_create(
                    product=purchase.product,
                    defaults={"quantity": 0}
                )

                inventory.quantity += purchase.quantity
                inventory.save()

            messages.success(
                request,
                f"Purchase recorded successfully. "
                f"{purchase.quantity} {purchase.product.unit} "
                f"of {purchase.product.name} added to stock."
            )
            log_activity(
                request,
                'purchase_created',
                f'Purchase recorded: {purchase.quantity} {purchase.product.unit} '
                f'of {purchase.product.name}',
                target_type='Purchase',
                target_id=purchase.id,
            )

            return redirect("purchase_list")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        # Pre-fill the form with the preselected product
        initial_data = {}
        if preselected_product_id:
            initial_data['product'] = preselected_product_id

        form = PurchaseForm(initial=initial_data)

    purchases = Purchase.objects.select_related(
        "supplier",
        "product"
    ).order_by("-purchase_date")

    return render(
        request,
        "purchases/purchase_list.html",
        {
            "form": form,
            "purchases": purchases,
            "preselected_product_id": preselected_product_id,
        }
    )