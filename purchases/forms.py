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
                "class": "form-control",
                "min": "1",
                "placeholder": "Enter quantity"
            }),

            "buying_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Enter buying price"
            }),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity

    def clean_buying_price(self):
        price = self.cleaned_data["buying_price"]

        if price < 0:
            raise forms.ValidationError(
                "Buying price cannot be negative."
            )

        return price