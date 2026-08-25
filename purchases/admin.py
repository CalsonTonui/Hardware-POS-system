from django.contrib import admin
from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "supplier",
        "product",
        "quantity",
        "buying_price",
        "purchase_date",
    )

    list_filter = (
        "supplier",
        "purchase_date",
    )

    search_fields = (
        "product__name",
        "supplier__name",
    )