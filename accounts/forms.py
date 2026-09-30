from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


User = get_user_model()


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'is_active',
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username',
            }),

            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
            }),

            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
            }),

            'role': forms.Select(attrs={
                'class': 'form-select',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class UserUpdateForm(UserChangeForm):

    password = None

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'is_active',
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'role': forms.Select(attrs={
                'class': 'form-select',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }