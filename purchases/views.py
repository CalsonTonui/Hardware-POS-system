from django.shortcuts import render, redirect
from .models import Purchase
from .forms import PurchaseForm
from inventory.models import Inventory


def purchase_list(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST)

        if form.is_valid():
            purchase = form.save()

            inventory, created = Inventory.objects.get_or_create(
                product=purchase.product
            )

            inventory.quantity += purchase.quantity
            inventory.save()

            return redirect("purchase_list")

    else:
        form = PurchaseForm()

    purchases = Purchase.objects.all().order_by("-purchase_date")

    return render(request,
                  "purchases/purchase_list.html",
                  {
                      "form": form,
                      "purchases": purchases,
                  })