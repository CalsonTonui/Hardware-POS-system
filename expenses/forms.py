from django import forms
from .models import Expense


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            'title',
            'category',
            'amount',
            'description',
            'expense_date',
        ]

        widgets = {

            'title': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'category': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter amount',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter description (optional)',
                    'rows': 3
                }
            ),

            'expense_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Blank first option
        self.fields['title'].choices = [
            ('', 'Select expense title')
        ] + list(Expense.EXPENSE_TITLE_CHOICES)

        self.fields['category'].choices = [
            ('', 'Select category')
        ] + list(Expense.CATEGORY_CHOICES)