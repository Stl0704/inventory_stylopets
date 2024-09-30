from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetView
from .forms import RegistroForm, InicioSesionForm, RecuperacionPasswordForm
from .models import *


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = True  # Cambia esto si deseas verificar el email
            usuario.save()
            login(request, usuario)
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


def inicio_sesion(request):
    if request.method == 'POST':
        form = InicioSesionForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('panel')
    else:
        form = InicioSesionForm()
    return render(request, 'inicio_sesion.html', {'form': form})


class RecuperacionPasswordView(auth_views.PasswordResetView):
    form_class = RecuperacionPasswordForm
    template_name = 'password_reset.html'


def cerrar_sesion(request):
    logout(request)
    return redirect('index')

def index(request):
    return render(request, 'index.html')
