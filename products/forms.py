from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    # Checkbox to remove the existing image
    remove_image = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'image-remove-checkbox',
            'id': 'removeImageCheckbox',
        }),
        label='Remove current image',
    )

    class Meta:
        model = Product

        fields = [
            'name',
            'category',
            'unit',
            'barcode',
            'buying_price',
            'selling_price',
            'image',
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
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        if barcode:
            return barcode.strip()
        return None