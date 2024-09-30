from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('panel/', views.Panel, name='panel'),
    path('procesar-codigo/', views.procesar_codigo, name='procesar_codigo'),
    path('buscar-producto/', views.buscar_producto, name='buscar_producto'),
    path('cancelar-ingreso/', views.cancelar_ingreso, name='cancelar_ingreso'),  # Nueva ruta para cancelar
    path('confirmar-ingreso/', views.confirmar_ingreso, name='confirmar_ingreso'),
    path('cancelar-ingreso/', views.cancelar_ingreso, name='cancelar_ingreso'),
]
