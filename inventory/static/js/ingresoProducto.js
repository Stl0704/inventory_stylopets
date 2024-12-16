// ingresoProducto.js

console.log('ingresoProducto.js cargado correctamente.');

// Array único para manejar los productos en el carrito
let productos = [];

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para actualizar la lista de productos en la interfaz
function actualizarListaProductos() {
    const listaProductos = document.getElementById('productos-list');
    listaProductos.innerHTML = '';  // Limpiar la lista antes de actualizarla

    productos.forEach(producto => {
        const productoHtml = `
            <li id="producto-${producto.Id_Producto}">
                <p><strong>Id Producto:</strong> ${producto.Id_Producto}</p>
                <p><strong>Nombre:</strong> ${producto.Nombre}</p>
                <p><strong>Categoría:</strong> ${producto.Categoria}</p>
                <input type="number" name="cantidad_${producto.SKU}" value="1" min="1" class="form-control mb-2" />
                <button type="button" class="btn btn-danger eliminar-btn" data-producto-id="${producto.Id_Producto}">Eliminar</button>
            </li>
        `;
        listaProductos.insertAdjacentHTML('beforeend', productoHtml);
    });

    addEliminarEvento(); // Asegurarse de que los botones "Eliminar" funcionen
}

// Función para manejar la eliminación de productos
function addEliminarEvento() {
    const eliminarBtns = document.querySelectorAll('.eliminar-btn');
    eliminarBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const idProducto = btn.getAttribute('data-producto-id');
            eliminarProducto(idProducto);
        });
    });
}

function eliminarProducto(idProducto) {
    productos = productos.filter(producto => producto.Id_Producto != idProducto);
    actualizarListaProductos();
    console.log(`Producto con ID ${idProducto} eliminado del carrito.`);
}

// Manejar la búsqueda manual por SKU o ID
document.getElementById('buscar-producto-btn').addEventListener('click', () => {
    const skuId = document.getElementById('sku-id').value.trim();
    if (skuId) {
        console.log(`Buscando producto con SKU/ID: ${skuId}`);
        fetch(`/inventory/buscar-producto/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')  // Obtener el token CSRF
            },
            body: new URLSearchParams({ 'sku_id': skuId })
        })
            .then(response => response.json())  // Asegurarse de que la vista 'buscar_producto' devuelve JSON
            .then(data => {
                console.log('Respuesta del servidor:', data);
                if (data.producto) {
                    console.log(`Producto encontrado: ${data.producto.Nombre}`);
                    // Añadir el producto al carrito
                    productos.push(data.producto);
                    actualizarListaProductos();
                    alert(`Producto añadido: ${data.producto.Nombre}`);
                } else if (data.error) {
                    console.log(`Error del servidor: ${data.error}`);
                    alert(`Error: ${data.error}`);
                } else {
                    console.log('Respuesta inesperada del servidor:', data);
                    alert('Respuesta inesperada del servidor.');
                }
            })
            .catch(error => console.error('Error al buscar el producto:', error));
    } else {
        alert('Por favor, ingresa un SKU o ID válido.');
    }
});

// Manejar el envío del formulario para subir la imagen del código de barras
document.getElementById('escanear-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevenir el envío normal del formulario

    let formData = new FormData(this); // Crear un FormData del formulario

    // Realizar la solicitud usando fetch()
    fetch('/inventory/escanear-codigo/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')  // Incluir el token CSRF
        },
        body: formData
    })
        .then(response => response.json()) // Asegurarse de que la vista 'procesar-codigo' devuelve JSON
        .then(data => {
            if (data.producto) {
                // Mostrar un alert de confirmación
                alert('Producto añadido: ' + data.producto.Nombre);

                // Añadir el producto al array y actualizar la lista visualmente
                productos.push(data.producto);
                actualizarListaProductos(); // Esta función ya la tienes implementada y actualiza la lista
                console.log(`Producto ${data.producto.Nombre} añadido al carrito desde la subida de imagen.`);
            } else if (data.error) {
                alert(data.error);
                console.log(`Error del servidor: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error al escanear el producto:', error);
            alert('Ocurrió un error al intentar escanear el producto.');
        });
});

// Cancelar Ingreso
document.getElementById('cancelar-ingreso-btn').addEventListener('click', () => {
    if (confirm('¿Estás seguro de cancelar el ingreso?')) {
        // Hacemos una solicitud para vaciar la lista de productos en el servidor
        fetch('/inventory/cancelar-ingreso/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Obtener el token CSRF
            }
        })
            .then(response => {
                if (response.ok) {
                    // Redirigir al usuario al panel
                    window.location.href = '/inventory/panel/';
                } else {
                    response.json().then(data => {
                        alert(`Error: ${data.error || 'Error desconocido al cancelar el ingreso.'}`);
                    });
                }
            })
            .catch(error => {
                console.error('Error al procesar la cancelación del ingreso:', error);
                alert('Error en la solicitud para cancelar el ingreso.');
            });
    }
});

// Manejar la búsqueda fija del producto con Id_Producto = 1001
document.getElementById('obtener-btn').addEventListener('click', () => {
    const codigoFijo = '1001';
    console.log(`Enviando código fijo: ${codigoFijo}`);

    // Enviar el código fijo al backend utilizando el mismo endpoint que la búsqueda manual
    fetch(`/inventory/buscar-producto/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')  // Obtener el token CSRF
        },
        body: new URLSearchParams({ 'sku_id': codigoFijo })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.producto) {
            console.log(`Producto encontrado: ${data.producto.Nombre}`);
            // Añadir el producto al carrito
            productos.push(data.producto);
            actualizarListaProductos();
            alert(`Producto añadido: ${data.producto.Nombre}`);
        } else if (data.error) {
            console.log(`Error del servidor: ${data.error}`);
            alert(`Error: ${data.error}`);
        } else {
            console.log('Respuesta inesperada del servidor:', data);
            alert('Respuesta inesperada del servidor.');
        }
        window.location.reload(false);
    })
    .catch(error => {
        console.error('Error al procesar el código fijo:', error);
        window.location.reload(false);
    });
    
});

// Funcionalidad de Escaneo con la Cámara usando zxing-js
(function() {
    console.log('Funcionalidad de escaneo con cámara cargada.');

    // Obtener referencias a los elementos del DOM
    const video = document.getElementById('camera-stream');
    const obtenerBtn = document.getElementById('obtener-btn');
    const stopCameraBtn = document.getElementById('stop-camera-btn');
    const capturedImage = document.getElementById('captured-image'); // Elemento para mostrar la imagen capturada
    let stream = null;

    // Crear un lector de códigos
    const codeReader = new ZXing.BrowserQRCodeReader();
    console.log('zxing-js cargado correctamente.');

    // Función para iniciar la cámara y empezar a escanear
    function startCameraAndScan() {
        console.log('Iniciando escaneo de QR con zxing-js...');
        codeReader.decodeFromVideoDevice(null, 'camera-stream', (result, error) => {
            if (result) {
                console.log('Código QR detectado:', result.text);
                
                // *** Usar un código fijo en lugar del código detectado ***
                const codigoFijo = '1001';
                console.log(`Usando código fijo: ${codigoFijo}`);

                // Enviar el código fijo al backend utilizando el endpoint de búsqueda manual
                fetch(`/inventory/buscar-producto/`, { // Utilizamos el mismo endpoint que la búsqueda manual
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: new URLSearchParams({ 'sku_id': codigoFijo })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Respuesta del servidor:', data);
                    if (data.producto) {
                        console.log(`Producto encontrado: ${data.producto.Nombre}`);
                        alert(`Producto encontrado: ${data.producto.Nombre}`);
                        // Añadir el producto al carrito
                        productos.push(data.producto);
                        actualizarListaProductos();
                        console.log(`Producto ${data.producto.Nombre} añadido al carrito.`);
                        // Detener el escaneo
                        codeReader.reset();
                    } else if (data.error) {
                        console.log(`Error del servidor: ${data.error}`);
                        alert(`Error: ${data.error}`);
                    } else {
                        console.log('Respuesta inesperada del servidor:', data);
                        alert('Respuesta inesperada del servidor.');
                    }
                })
                .catch(error => {
                    console.error('Error al procesar el código fijo:', error);
                    alert('Hubo un problema al procesar el código.');
                });
            }
            if (error && !(error instanceof ZXing.NotFoundException)) {
                console.error('Error al escanear el QR:', error);
                alert('Error al escanear el QR. Intenta nuevamente.');
            }
        });
    }

    // Evento para el botón "Escanear"
    document.getElementById('capture-btn').addEventListener('click', () => {
        console.log('Botón "Escanear" clicado.');

        if (!stream) {  // Solo iniciamos la cámara si no está activa
            console.log('No hay stream activo. Iniciando escaneo...');
            startCameraAndScan();
        } else {
            console.log('Escaneo ya está activo.');
        }
    });

    // Evento para el botón "Obtener" para traer el producto con ID 1001
    obtenerBtn.addEventListener('click', () => {
        console.log('Botón "Obtener" clicado.');

        const codigoFijo = '1001';
        console.log(`Enviando código fijo: ${codigoFijo}`);
        alert(`Código fijo enviado: ${codigoFijo}`);

        // Enviar el código fijo al backend utilizando el mismo endpoint que la búsqueda manual
        fetch(`/inventory/buscar-producto/`, { // Utilizamos el mismo endpoint que la búsqueda manual
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({ 'sku_id': codigoFijo })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor:', data);
            if (data.producto) {
                console.log(`Producto encontrado: ${data.producto.Nombre}`);
                alert(`Producto encontrado: ${data.producto.Nombre}`);
                // Añadir el producto al carrito
                productos.push(data.producto);
                actualizarListaProductos();
                console.log(`Producto ${data.producto.Nombre} añadido al carrito.`);
                // Detener el escaneo si está activo
                if (codeReader) {
                    codeReader.reset();
                }
            } else if (data.error) {
                console.log(`Error del servidor: ${data.error}`);
                alert(`Error: ${data.error}`);
            } else {
                console.log('Respuesta inesperada del servidor:', data);
                alert('Respuesta inesperada del servidor.');
            }
        })
        .catch(error => {
            console.error('Error al procesar el código fijo:', error);
            alert('Hubo un problema al procesar el código.');
        });
    });

    

    console.log('Funcionalidad de escaneo con cámara cargada.');
})();

// Evento para el botón "Cerrar Escáner"
stopCameraBtn.addEventListener('click', () => {
    console.log('Botón "Cerrar Escáner" clicado.');
    if (codeReader) {
        codeReader.reset();
        console.log('Escaneo detenido.');
    }

    // Limpiar el array de productos y actualizar la interfaz
    productos = [];
    actualizarListaProductos();
    console.log('Carrito limpiado en el frontend.');

    // Ocultar el botón "Obtener" y la imagen capturada
    obtenerBtn.style.display = 'none';
    capturedImage.style.display = 'none';
    console.log('Botón "Obtener" y imagen capturada ocultados.');
});


