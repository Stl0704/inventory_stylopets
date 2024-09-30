from django.shortcuts import render

# Create your views here.


# PRUEBA STATIC RENDER

def Inicio(request):
    return render(request, "index.html")


# LOGIN USUARIOS


# PRUEBA LOBBY:

def Lobby(request):
    return render(request, "lobby.html")
