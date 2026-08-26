from django import forms
from .models import Sale


class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale

        fields = [
            'product',
            'quantity',
            'payment_method',
        ]

        widgets = {

            'product': forms.Select(attrs={
                'class': 'form-select'
            }),

            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity'
            }),

            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
        }