from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "class": "input",
            "placeholder": "Correo electrónico",
            "autocomplete": "email"
        })
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "Contraseña",
            "autocomplete": "current-password"
        })
    )