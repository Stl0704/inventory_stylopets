from django.shortcuts import render

# Create your views here.


# PRUEBA STATIC

def Inicio(request):
    return render(request, "index.html")
