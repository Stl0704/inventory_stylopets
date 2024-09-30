let productos = [];

document.getElementById('buscar-producto-btn').addEventListener('click', () => {
    const skuId = document.getElementById('sku-id').value;
    if (skuId) {
        fetch(`/buscar-producto?query=${skuId}`)
        .then(response => response.json())
        .then(data => {
            if (data.producto) {
                // Añadir producto a la lista de ingreso
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
            'X-CSRFToken': csrftoken  // Necesitas manejar el token CSRF
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
        window.location.href = '/panel/';
    }
});


document.getElementById('cancelar-ingreso-btn').addEventListener('click', function() {
    // Hacemos una solicitud para cancelar el ingreso y limpiar la lista
    window.location.href = '/inventory/cancelar-ingreso/';
});
