from django import forms
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import Material
from accounts.models import CustomUser


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


class ContactDataForm(forms.ModelForm):
    class Meta:
        model = CustomUser

        fields = [
            "nombre_pila",
            "apellido_paterno",
            "apellido_materno",
            "email",
        ]

        labels = {
            "nombre_pila": "Nombre(s)",
            "apellido_paterno": "Apellido paterno",
            "apellido_materno": "Apellido materno",
            "email": "Correo electrónico",
        }

        widgets = {
            "nombre_pila": forms.TextInput(attrs={
                "class": "contact-input",
                "placeholder": "Nombre(s)",
                "autocomplete": "given-name"
            }),
            "apellido_paterno": forms.TextInput(attrs={
                "class": "contact-input",
                "placeholder": "Apellido paterno",
                "autocomplete": "family-name"
            }),
            "apellido_materno": forms.TextInput(attrs={
                "class": "contact-input",
                "placeholder": "Apellido materno",
                "autocomplete": "additional-name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "contact-input",
                "placeholder": "Correo electrónico",
                "autocomplete": "email"
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Ese correo ya está registrado por otro usuario.")

        return email


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
                'accept': '.pdf,.doc,.docx, .txt, .odt',
                'required': 'true'
            })
        }