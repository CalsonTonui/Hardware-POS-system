from django import forms
from .models import Purchase


class PurchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase
        fields = [
            "supplier",
            "product",
            "quantity",
            "buying_price",
        ]

        widgets = {
            "supplier": forms.Select(attrs={
                "class": "form-select"
            }),

            "product": forms.Select(attrs={
                "class": "form-select"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "buying_price": forms.NumberInput(attrs={
                "class": "form-control"
            }),
        }