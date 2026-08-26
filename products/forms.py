from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'category',
            'unit',
            'barcode',
            'buying_price',
            'selling_price',
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),

            'category': forms.Select(attrs={
                'class': 'form-select'
            }),

            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),

            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional - leave blank if none'
            }),

            'buying_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter buying price',
                'step': '0.01',
                'min': '0'
            }),

            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter selling price',
                'step': '0.01',
                'min': '0'
            }),
        }

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')

        if barcode:
            return barcode.strip()

        return None