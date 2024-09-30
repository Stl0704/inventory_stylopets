from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido',
                  'rol', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'user-box', 'required': True}),
            'nombre': forms.TextInput(attrs={'class': 'user-box', 'required': True}),
            'apellido': forms.TextInput(attrs={'class': 'user-box', 'required': True}),
            'rol': forms.Select(attrs={'class': 'user-box', 'required': True}),
            'password1': forms.PasswordInput(attrs={'class': 'user-box', 'required': True}),
            'password2': forms.PasswordInput(attrs={'class': 'user-box', 'required': True}),
        }
        labels = {
            'email': 'Correo Electrónico',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'rol': 'Rol',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }


class InicioSesionForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'user-box',
            'required': True,
            'autocomplete': 'email',
        }),
        label='',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'user-box',
            'required': True,
            'autocomplete': 'current-password',
        }),
        label='',
    )


class RecuperacionPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'user-box', 'required': True}),
        label='Correo Electrónico',
    )
