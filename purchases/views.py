from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from .models import Purchase
from .forms import PurchaseForm
from inventory.models import Inventory


def purchase_list(request):

    if request.method == "POST":

        form = PurchaseForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                purchase = form.save()

                inventory, created = Inventory.objects.get_or_create(
                    product=purchase.product,
                    defaults={
                        "quantity": 0
                    }
                )

                inventory.quantity += purchase.quantity
                inventory.save()

            messages.success(
                request,
                f"Purchase recorded successfully. "
                f"{purchase.quantity} {purchase.product.unit} "
                f"of {purchase.product.name} added to stock."
            )

            return redirect("purchase_list")

    else:

        form = PurchaseForm()

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
        }
    )