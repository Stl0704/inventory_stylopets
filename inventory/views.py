from django.shortcuts import render, get_object_or_404
from .models import IngresoTest, DetalleIngresoTest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseBadRequest, JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image, ImageOps
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


# PROCESAR IMAGEN

# Función auxiliar para procesar el código desde una imagen


def procesar_codigo_imagen(image_file):
    try:
        # Abrir la imagen proporcionada
        image = Image.open(image_file)

        # Convertir la imagen a escala de grises para mejorar la lectura
        image = ImageOps.grayscale(image)

        # Procesar la imagen para encontrar el código de barras o QR
        decoded_objects = decode(image)

        if decoded_objects:
            # Obtenemos el primer código encontrado y lo decodificamos
            codigo = decoded_objects[0].data.decode('utf-8')
            print(f"Código detectado: {codigo}")  # depurado
            return codigo
        else:
            print("No se detectó ningún código en la imagen.")
            return None
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return render(request, 'registrarIngreso.html', {'productos_añadidos': productos_añadidos})

# Nueva vista para procesar el escaneo de la imagen (QR/Código de barras)


@csrf_exempt
def escanear_codigo(request):
    producto = None
    error = None

    # Obtener la lista de productos añadidos a la sesión o inicializar una lista vacía
    productos_añadidos = request.session.get('productos_añadidos', [])

    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        # Utilizar la nueva función para procesar el código de la imagen
        codigo = procesar_codigo_imagen(image_file)

        if codigo:
            # Intentamos buscar el código primero como SKU
            producto = ProductoTests.objects.filter(SKU=codigo).first()

            # Si no se encuentra como SKU, buscar como Id_Producto
            if not producto and codigo.isdigit():
                producto = ProductoTests.objects.filter(
                    Id_Producto=codigo).first()

            if producto:
                # Verificar si el producto ya está en la lista de productos añadidos
                producto_ya_añadido = any(
                    p['Id_Producto'] == producto.Id_Producto for p in productos_añadidos)

                if not producto_ya_añadido:
                    producto_data = {
                        'Id_Producto': producto.Id_Producto,
                        'SKU': producto.SKU,
                        'Nombre': producto.Nombre,
                        'Categoria': producto.Categoria,
                        'Stock': producto.Stock
                    }
                    productos_añadidos.append(producto_data)
                    request.session['productos_añadidos'] = productos_añadidos
                    return JsonResponse({'producto': producto_data})
                else:
                    error = 'El producto ya está en la lista de productos añadidos.'
            else:
                error = 'No se encontró ningún producto con el código escaneado.'
        else:
            error = 'No se encontró ningún código en la imagen.'

    return render(request, 'registrarIngreso.html', {'productos_añadidos': productos_añadidos})


# Vista para procesar el registro de ingreso
def procesar_ingreso(request):
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
                producto_obj = ProductoTests.objects.get(
                    Id_Producto=producto['Id_Producto'])
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
            return redirect('inventory/panel')

        else:
            return render(request, 'registrarIngreso.html', {'error': 'No hay productos añadidos para confirmar.'})

    return render(request, 'registrarIngreso.html', {'productos_añadidos': productos_añadidos})


# Cancelar ingreso
def cancelar_ingreso(request):
    if request.method == 'POST':
        # Vaciar la lista de productos añadidos en la sesión
        request.session['productos_añadidos'] = []
        # Redirigir al panel
        # Devuelve una respuesta JSON para confirmar la operación
        return JsonResponse({'success': True})
    return redirect('panel')


def confirmar_ingreso(request):
    if request.method == 'POST':
        productos_añadidos = request.session.get('productos_añadidos', [])

        if productos_añadidos:
            responsable = f"{request.user.nombre} {request.user.apellido}"

            nuevo_ingreso = IngresoTest(responsable=responsable)
            nuevo_ingreso.save()

            for producto in productos_añadidos:
                # Obtener la cantidad desde el formulario
                cantidad_key = f'cantidad_{producto["SKU"]}'
                # Si no se envía, el valor predeterminado será 1
                cantidad = int(request.POST.get(cantidad_key, 1))

                # Actualizar el stock del producto
                producto_obj = ProductoTests.objects.get(
                    Id_Producto=producto['Id_Producto'])
                producto_obj.Stock += cantidad
                producto_obj.save()

                # Crear el detalle de ingreso
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

            # Limpiar la lista de productos añadidos
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
        productos_añadidos = [
            producto for producto in productos_añadidos if producto['Id_Producto'] != int(producto_id)]

        # Actualizar la lista en la sesión
        request.session['productos_añadidos'] = productos_añadidos

        # Confirmar la operación y enviar la lista actualizada
        return JsonResponse({'success': True, 'productos_actualizados': productos_añadidos})
    except Exception as e:
        # Enviar una respuesta en caso de error
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
def buscar_producto(request):
    producto = None
    error = None

    # Obtener la lista de productos añadidos a la sesión o inicializar una lista vacía
    productos_añadidos = request.session.get('productos_añadidos', [])

    if request.method == 'POST':
        query = request.POST.get('sku_id', '')

        if query:
            # Buscar el producto por SKU o ID
            producto = ProductoTests.objects.filter(Id_Producto=query).first(
            ) or ProductoTests.objects.filter(SKU=query).first()

            if producto:
                # Verificar si el producto ya está en la lista de productos añadidos
                producto_ya_añadido = any(
                    p['Id_Producto'] == producto.Id_Producto for p in productos_añadidos)

                if not producto_ya_añadido:
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
                else:
                    error = 'El producto ya está en la lista de productos añadidos.'
            else:
                error = 'Producto no encontrado.'

    return render(request, 'registrarIngreso.html', {'productos_añadidos': productos_añadidos, 'error': error})


def listar_guiasDespacho(request):
    ingresos = HistorialIngresosTests.objects.all()
    return render(request, 'listado_GuiaDespacho.html', {'ingresos': ingresos})


# Vista para mostrar el detalle de un ingreso específico
def ver_GuiaDespacho(request, ingreso_id):
    ingreso = get_object_or_404(IngresoTest, id_ingreso=ingreso_id)
    detalles = DetalleIngresoTest.objects.filter(ingreso=ingreso)
    return render(request, 'recibir.html', {'ingreso': ingreso, 'detalles': detalles})


def redirigir_guia_despacho(request):
    if request.method == "POST":
        ingreso_id = request.POST.get("ingreso_id")
        # Verifica el valor en la consola
        print("Ingreso ID recibido:", ingreso_id)

        # Verifica si ingreso_id tiene un valor
        if ingreso_id:
            return redirect(reverse('ver_GuiaDespacho', args=[ingreso_id]))
        else:
            # Retorna una respuesta de error si ingreso_id está vacío
            return HttpResponseBadRequest("ID de ingreso no proporcionado.")
    else:
        return redirect('listado_GuiaDespacho')
