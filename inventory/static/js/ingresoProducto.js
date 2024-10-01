let productos = [];

// Buscar producto por SKU o ID
document.getElementById('buscar-producto-btn').addEventListener('click', () => {
    const skuId = document.getElementById('sku-id').value;
    if (skuId) {
        fetch(`/buscar-producto?query=${skuId}`)
            .then(response => response.json())
            .then(data => {
                if (data.producto) {
                    const productoHtml = `
                        <div class="producto-entry">
                            <span>${data.producto.Nombre} (${data.producto.SKU})</span>
                            <input type="number" name="cantidad_${data.producto.SKU}" value="1" min="1" />
                        </div>
                    `;
                    document.getElementById('productos-list').insertAdjacentHTML('beforeend', productoHtml);
                    productos.push(data.producto);
                } else {
                    alert('Producto no encontrado');
                }
            });
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

    fetch('/procesar-ingreso/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Necesitas manejar el token CSRF
        },
        body: JSON.stringify(ingresoData)
    }).then(response => {
        if (response.ok) {
            alert('Ingreso registrado exitosamente');
            window.location.href = '/panel/';
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