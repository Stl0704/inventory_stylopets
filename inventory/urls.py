from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('panel/', views.Panel, name='panel'),
    path('procesar-ingreso/', views.procesar_ingreso, name='procesar_ingreso'),
    path('escanear-codigo/', views.escanear_codigo, name='escanear_codigo'),  # Nueva URL para subir imagen y escanear código
    path('buscar-producto/', views.buscar_producto, name='buscar_producto'),
    path('confirmar-ingreso/', views.confirmar_ingreso, name='confirmar_ingreso'),
    path('cancelar-ingreso/', views.cancelar_ingreso, name='cancelar_ingreso'),
    path('historial-ingresos/', views.historial_ingresos, name='historial_ingresos'),
    path('eliminar-producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('obtener-productos/', views.obtener_productos, name='obtener_productos'),  # Nueva ruta
]
