from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido',
                  'rol', 'password1', 'password2')


class InicioSesionForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'required': '',
            'class': '',
        }),
        label='',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'required': '',
            'class': '',
        }),
        label='',
    )


class RecuperacionPasswordForm(PasswordResetForm):
    pass  # Puedes personalizar este formulario si lo deseas.
