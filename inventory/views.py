from django.shortcuts import render,redirect
from django.http import JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image
from .models import ProductoTests,IngresoTest,DetalleIngresoTest,HistorialIngresosTests
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone


# Create your views here.
def Panel(request):
    return render(request, "panel.html")

def Inicio(request):
    return render(request, "index.html")

def procesar_codigo(request):
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


def buscar_producto(request):
    query = request.GET.get('query', '')  # Obtenemos el valor del input de búsqueda
    producto = None
    
    if query.isdigit():  # Si el query es un número, buscar por Id_Producto
        producto = ProductoTests.objects.filter(Id_Producto=query).first()
    else:  # Si es un string, buscar por SKU
        producto = ProductoTests.objects.filter(SKU=query).first()

    return render(request, 'registrarIngreso.html', {'producto': producto, 'query': query})

def confirmar_ingreso(request):
    if request.method == 'POST':
        productos_añadidos = request.session.get('productos_añadidos', [])

        if productos_añadidos:
            # Obtenemos el responsable usando el nombre y apellido del usuario
            responsable = f"{request.user.nombre} {request.user.apellido}"

            # Primero, creamos el ingreso principal en la tabla IngresoTest
            nuevo_ingreso = IngresoTest(
                responsable=responsable
            )
            nuevo_ingreso.save()  # Guardamos el ingreso principal y generamos un Id_Ingreso

            # Guardamos los detalles del ingreso en la tabla DetalleIngresoTest
            for index, producto in enumerate(productos_añadidos, start=1):
                producto_obj = ProductoTests.objects.get(Id_Producto=producto['Id_Producto'])

                # Obtenemos la cantidad ingresada desde el formulario
                cantidad_key = f'cantidad_{index}'
                cantidad = int(request.POST.get(cantidad_key, 1))  # Por defecto es 1 si no hay cantidad ingresada

                # Actualizamos el stock del producto
                producto_obj.Stock += cantidad
                producto_obj.save()

                # Guardamos el detalle del ingreso en DetalleIngresoTest
                DetalleIngresoTest.objects.create(
                    ingreso=nuevo_ingreso,  # Relacionamos el detalle con el ingreso principal
                    producto=producto_obj,  # Relacionamos el detalle con el producto
                    cantidad=cantidad  # Almacenamos la cantidad de stock entrante
                )

            # Finalmente, creamos un registro en HistorialIngresosTests con el Id_Ingreso generado
            HistorialIngresosTests.objects.create(
                Id_Ingreso=nuevo_ingreso,  # Relacionamos con el ingreso recién creado (IngresoTest)
                responsable=responsable,   # Almacenamos el responsable
                fecha=nuevo_ingreso.fecha  # Guardamos la fecha del ingreso
            )

            # Limpiamos la sesión después de guardar el ingreso
            request.session['productos_añadidos'] = []

            # Redirigimos al panel
            return redirect('panel')

        else:
            return render(request, 'registrarIngreso.html', {'error': 'No hay productos añadidos para confirmar.'})

    return redirect('panel')


def cancelar_ingreso(request):
    # Limpia la lista de productos añadidos en la sesión
    request.session['productos_añadidos'] = []
    return redirect('panel')



# def buscar_producto(request):
#     query = request.GET.get('query', '')  # Obtenemos el valor del input de búsqueda
#     resultado = None
    
#     if query.isdigit():  # Si el query es un número, buscar por Id_Producto
#         resultado = ProductoTests.objects.filter(Id_Producto=query).first()
#     else:  # Si es un string, buscar por SKU
#         resultado = ProductoTests.objects.filter(SKU=query).first()

#     return render(request, 'buscarProducto.html', {'producto': resultado, 'query': query})