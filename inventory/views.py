from django.shortcuts import render, redirect
from django.http import JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image
from .models import ProductoTests, IngresoTest, DetalleIngresoTest, HistorialIngresosTests
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST


# Vista para el panel principal
def Panel(request):
    return render(request, "panel.html")

def Inicio(request):
    return render(request, "index.html")


@csrf_exempt
def obtener_productos(request):
    productos_añadidos = request.session.get('productos_añadidos', [])
    return JsonResponse({'productos': productos_añadidos})


# Nueva vista para procesar el escaneo de la imagen (QR/Código de barras)
@csrf_exempt
def escanear_codigo(request):
    producto = None
    error = None
    
    # Obtener la lista de productos añadidos a la sesión o inicializar una lista vacía
    productos_añadidos = request.session.get('productos_añadidos', [])
    
    if request.method == 'POST' and request.FILES['image']:
        image_file = request.FILES['image']
        image = Image.open(image_file)

        # Procesar la imagen para encontrar el código de barras o QR
        decoded_objects = decode(image)
        if decoded_objects:
            codigo = decoded_objects[0].data.decode('utf-8')  # Obtenemos el código

            # Intentamos buscar el código en la base de datos
            if codigo.isdigit():  # Si el código es numérico, puede ser un Id_Producto
                producto = ProductoTests.objects.filter(Id_Producto=codigo).first()
            else:  # Si es texto, buscar por SKU
                producto = ProductoTests.objects.filter(SKU=codigo).first()

            if producto:
                # Añadir el producto a la lista de productos añadidos
                productos_añadidos.append({
                    'Id_Producto': producto.Id_Producto,
                    'SKU': producto.SKU,
                    'Nombre': producto.Nombre,
                    'Categoria': producto.Categoria,
                    'Stock': producto.Stock
                })
                # Guardar la lista actualizada en la sesión
                request.session['productos_añadidos'] = productos_añadidos
            else:
                error = 'No se encontró ningún producto con el código escaneado.'
        else:
            error = 'No se encontró ningún código en la imagen.'

    return render(request, 'registrarIngreso.html', {'producto': producto, 'error': error, 'productos_añadidos': productos_añadidos})


# Vista para procesar el registro de ingreso
def procesar_codigo(request):
    # Lógica para registrar ingreso
    productos_añadidos = request.session.get('productos_añadidos', [])
    
    if request.method == 'POST':
        # Procesar el registro de ingreso
        if productos_añadidos:
            responsable = f"{request.user.nombre} {request.user.apellido}"
            nuevo_ingreso = IngresoTest(responsable=responsable)
            nuevo_ingreso.save()

            # Procesar detalles del ingreso
            for index, producto in enumerate(productos_añadidos, start=1):
                producto_obj = ProductoTests.objects.get(Id_Producto=producto['Id_Producto'])
                cantidad_key = f'cantidad_{index}'
                cantidad = int(request.POST.get(cantidad_key, 1))
                producto_obj.Stock += cantidad
                producto_obj.save()

                # Crear registro de detalle del ingreso
                DetalleIngresoTest.objects.create(
                    ingreso=nuevo_ingreso,
                    producto=producto_obj,
                    cantidad=cantidad
                )

            # Registrar en el historial
            HistorialIngresosTests.objects.create(
                Id_Ingreso=nuevo_ingreso,
                responsable=responsable,
                fecha=nuevo_ingreso.fecha
            )

            # Limpiar la sesión después de confirmar el ingreso
            request.session['productos_añadidos'] = []
            return redirect('panel')

        else:
            return render(request, 'registrarIngreso.html', {'error': 'No hay productos añadidos para confirmar.'})

    return render(request, 'registrarIngreso.html', {'productos_añadidos': productos_añadidos})


# Cancelar ingreso
def cancelar_ingreso(request):
    if request.method == 'POST':
        # Vaciar la lista de productos añadidos en la sesión
        request.session['productos_añadidos'] = []
        # Redirigir al panel
        return JsonResponse({'success': True})  # Devuelve una respuesta JSON para confirmar la operación
    return redirect('panel')

def confirmar_ingreso(request):
    if request.method == 'POST':
        productos_añadidos = request.session.get('productos_añadidos', [])

        if productos_añadidos:
            responsable = f"{request.user.nombre} {request.user.apellido}"

            nuevo_ingreso = IngresoTest(responsable=responsable)
            nuevo_ingreso.save()

            for index, producto in enumerate(productos_añadidos, start=1):
                producto_obj = ProductoTests.objects.get(Id_Producto=producto['Id_Producto'])
                cantidad_key = f'cantidad_{index}'
                cantidad = int(request.POST.get(cantidad_key, 1))

                producto_obj.Stock += cantidad
                producto_obj.save()

                DetalleIngresoTest.objects.create(
                    ingreso=nuevo_ingreso,
                    producto=producto_obj,
                    cantidad=cantidad
                )

            HistorialIngresosTests.objects.create(
                Id_Ingreso=nuevo_ingreso,
                responsable=responsable,
                fecha=nuevo_ingreso.fecha
            )

            request.session['productos_añadidos'] = []
            return redirect('panel')

        else:
            return render(request, 'registrarIngreso.html', {'error': 'No hay productos añadidos para confirmar.'})

    return redirect('panel')


# Ver historial de ingresos
def historial_ingresos(request):
    historial = HistorialIngresosTests.objects.all()
    return render(request, 'historialIngresos.html', {'historial': historial})


# Eliminar producto añadido al ingreso
@require_POST
def eliminar_producto(request, producto_id):
    try:
        # Obtener la lista de productos añadidos desde la sesión
        productos_añadidos = request.session.get('productos_añadidos', [])

        # Filtrar para eliminar el producto con el ID proporcionado
        productos_añadidos = [producto for producto in productos_añadidos if producto['Id_Producto'] != int(producto_id)]

        # Actualizar la lista en la sesión
        request.session['productos_añadidos'] = productos_añadidos

        # Confirmar la operación y enviar la lista actualizada
        return JsonResponse({'success': True, 'productos_actualizados': productos_añadidos})
    except Exception as e:
        # Enviar una respuesta en caso de error
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def buscar_producto(request):
    query = request.GET.get('sku_id', '')
    productos_añadidos = request.session.get('productos_añadidos', [])

    if query:
        # Buscar el producto por SKU o ID
        producto = ProductoTests.objects.filter(Id_Producto=query).first() or ProductoTests.objects.filter(SKU=query).first()

        if producto:
            # Agregar el producto encontrado a la lista de productos añadidos
            productos_añadidos.append({
                'Id_Producto': producto.Id_Producto,
                'SKU': producto.SKU,
                'Nombre': producto.Nombre,
                'Categoria': producto.Categoria,
                'Stock': producto.Stock,
            })

            # Actualizar la lista de productos añadidos en la sesión
            request.session['productos_añadidos'] = productos_añadidos

    return render(request, 'registrarIngreso.html', {'productos_añadidos': productos_añadidos})
