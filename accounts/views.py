from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordResetView
from .forms import RegistroForm, InicioSesionForm
from .models import *


def Inicio(request):
    return render(request, "index.html")


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = True  # Puedes configurar la activación por correo si lo deseas
            usuario.save()
            login(request, usuario)
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'accounts/registro.html', {'form': form})


def inicio_sesion(request):
    if request.method == 'POST':
        form = InicioSesionForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            usuario = authenticate(request, email=email, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('home')
    else:
        form = InicioSesionForm()
    return render(request, 'accounts/inicio_sesion.html', {'form': form})


def cerrar_sesion(request):
    logout(request)
    return redirect('inicio_sesion')
