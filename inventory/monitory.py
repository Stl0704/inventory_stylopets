from django.shortcuts import render, redirect
from django.db import connection
from .forms import IpForm
from django.http import JsonResponse
import subprocess
from .models import Ip

# Create your views here.


def panel(request):
    return render(request, "principal.html")


def insertar_ip(request):
    if request.method == 'POST':
        form = IpForm(request.POST)
        if form.is_valid():
            grupo = form.cleaned_data['grupo']
            ip_address = form.cleaned_data['ip_address']
            name = form.cleaned_data['name']
            location = form.cleaned_data['location']
            status = form.cleaned_data['status']
            user_id = form.cleaned_data['user_id']

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ips (grupo, ip_address, name, location, status, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [grupo, ip_address, name, location, status, user_id])

            return redirect('index')

    else:
        form = IpForm()

    return render(request, 'agregar_IP.html', {'form': form})


def configurar_monitor(request):
    ips = Ip.objects.all()
    return render(request, 'configurar_monitor.html', {'ips': ips})


def ejecutar_ping(request):
    if request.method == "POST":
        ip_list = request.POST.getlist("ips")
        tipo_ping = request.POST.get("tipo_ping")

        resultados = {}
        for ip in ip_list:
            if tipo_ping == "rapido":
                result = subprocess.run(
                    ["ping", "-c", "1", ip], stdout=subprocess.PIPE)
            elif tipo_ping == "sostenido":
                result = subprocess.run(
                    ["ping", "-c", "5", ip], stdout=subprocess.PIPE)

            resultados[ip] = result.stdout.decode('utf-8')
        return JsonResponse(resultados)
