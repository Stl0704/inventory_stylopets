let productos = [];

document.addEventListener('DOMContentLoaded', () => {
    fetch(`/inventory/buscar-producto/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams({ 'sku_id': skuId })
    })
});

// Función para actualizar la lista de productos en la interfaza
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
}


// Buscar producto por SKU o ID
document.getElementById('buscar-producto-btn').addEventListener('click', () => {
    const skuId = document.getElementById('sku-id').value;
    if (skuId) {
        fetch(`/inventory/buscar-producto/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')  // Obtener el token CSRF
            },
            body: new URLSearchParams({ 'sku_id': skuId })
        })
            .then(response => response.text())  // Cambiar a texto para procesar la respuesta HTML
            .then(html => {
                document.body.innerHTML = html;  // Reemplazar el contenido del body con la respuesta actualizada
            })
            .catch(error => console.error('Error al buscar el producto:', error));
    }
});

// Escanear-form

document.addEventListener('DOMContentLoaded', () => {
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
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al escanear el producto');
                }
                return response.json(); // Procesar la respuesta como JSON
            })
            .then(data => {
                if (data.producto) {
                    // Mostrar un alert de confirmación
                    alert('Producto añadido: ' + data.producto.Nombre);

                    // Añadir el producto al array y actualizar la lista visualmente
                    productos.push(data.producto);
                    actualizarListaProductos(); // Esta función ya la tienes implementada y actualiza la lista
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error al escanear el producto:', error);
                alert('Ocurrió un error al intentar escanear el producto.');
            });
    });

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
    }

    // Obtener el token CSRF
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
});




// Confirmar Ingreso
document.getElementById('confirmar-ingreso-btn').addEventListener('click', () => {
    let ingresoData = {
        productos: []
    };

    productos.forEach(producto => {
        const cantidad = document.querySelector(`input[name="cantidad_${producto.SKU}"]`).value;
        ingresoData.productos.push({
            id_producto: producto.Id_Producto,
            cantidad: cantidad
        });
    });

    fetch('/inventory/procesar-ingreso/', {  // Cambiado a procesar-ingreso
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Manejar el token CSRF
        },
        body: JSON.stringify(ingresoData)
    }).then(response => {
        if (response.ok) {
            alert('Ingreso registrado exitosamente');
            window.location.href = '/inventory/panel/';
        }
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
                    window.location.href = '/inventory/panel';
                } else {
                    alert('Error al cancelar el ingreso.');
                }
            })
            .catch(error => {
                console.error('Error al procesar la cancelación del ingreso:', error);
                alert('Error en la solicitud para cancelar el ingreso.');
            });
    }
});

// Obtener el token CSRF
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