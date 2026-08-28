from django import forms
from .models import SystemSettings


class SettingsForm(forms.ModelForm):

    class Meta:

        model = SystemSettings

        fields = [
            'business_name',
            'business_phone',
            'business_email',
            'business_address',
            'business_location',
            'currency',
            'tax_rate',
            'low_stock_threshold',
            'receipt_footer',
            'show_business_phone',
            'show_business_address',
            'low_stock_notifications',
            'out_of_stock_notifications',
        ]

        widgets = {

            'business_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter business name'
                }
            ),

            'business_phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. 0712 345 678'
                }
            ),

            'business_email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'business@example.com'
                }
            ),

            'business_address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter business address'
                }
            ),

            'business_location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. Nairobi'
                }
            ),

            'currency': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. KSh'
                }
            ),

            'tax_rate': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Enter tax percentage'
                }
            ),

            'low_stock_threshold': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'placeholder': 'e.g. 5'
                }
            ),

            'receipt_footer': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Thank you for shopping with us.'
                }
            ),

            'show_business_phone': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'show_business_address': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'low_stock_notifications': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'out_of_stock_notifications': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }