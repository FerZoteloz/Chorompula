from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import Material


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

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['titulo', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Unidad 1 - Introducción',
                'required': 'true'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': '.pdf,.doc,.docx, .txt, .odt', # Restringimos a estos formatos
                'required': 'true'
            })
        }