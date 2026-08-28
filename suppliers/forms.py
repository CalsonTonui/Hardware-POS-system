
from django import forms

from .models import Supplier


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier

        fields = [
            'name',
            'phone',
            'address',
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter supplier name',
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number',
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter supplier address',
                    'rows': 3,
                }
            ),
        }
