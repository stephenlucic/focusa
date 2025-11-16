from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

GENDER_CHOICES = [
    ("", "Selecciona…"),
    ("M", "Masculino"),
    ("F", "Femenino"),
    ("O", "Otro"),
    ("N", "Prefiero no decir"),
]

COUNTRY_CHOICES = [
    ("", "Selecciona…"),
    ("Chile", "Chile"),
    ("Argentina", "Argentina"),
    ("Perú", "Perú"),
    ("México", "México"),
    ("Colombia", "Colombia"),
    ("España", "España"),
    ("Otro", "Otro"),
]

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name  = forms.CharField(label="Apellido", max_length=150, required=True)
    email      = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={
        "class": "form-control form-control-lg",
        "autocomplete": "email",
        "placeholder": "example@dominio.com",
    }))
    ocupacion  = forms.CharField(label="Ocupación", max_length=100, required=False)
    telefono   = forms.CharField(label="Teléfono", max_length=20, required=False, widget=forms.TextInput(attrs={
        "class": "form-control form-control-lg",
        "autocomplete": "tel",
        "placeholder": "+56 9 1234 5678",
    }))
    genero     = forms.ChoiceField(label="Género", choices=GENDER_CHOICES, required=False, widget=forms.Select(attrs={
        "class": "form-select form-select-lg",
    }))
    pais       = forms.ChoiceField(label="País", choices=COUNTRY_CHOICES, required=False, widget=forms.Select(attrs={
        "class": "form-select form-select-lg",
    }))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "ocupacion", "telefono", "genero", "pais", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        user.email      = self.cleaned_data["email"]
        if commit:
            user.save()
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    "ocupacion": self.cleaned_data.get("ocupacion", ""),
                    "telefono":  self.cleaned_data.get("telefono", ""),
                    "genero":    self.cleaned_data.get("genero", ""),
                    "pais":      self.cleaned_data.get("pais", ""),
                }
            )
        return user