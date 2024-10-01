// Lógica para procesar la imagen subida
const imageUploadForm = document.querySelector('form[enctype="multipart/form-data"]');
if (imageUploadForm) {
  imageUploadForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/procesar-codigo/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrftoken  // Necesario para manejar el token CSRF
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.producto) {
        // Lógica para agregar el producto a la lista
        const productoHtml = `
          <div class="producto-entry" id="producto-${data.producto.Id_Producto}">
            <span>${data.producto.Nombre} (${data.producto.SKU})</span>
            <input type="number" name="cantidad_${data.producto.SKU}" value="1" min="1" class="form-control" />
            <button type="button" class="btn btn-danger eliminar-btn" data-producto-id="${data.producto.Id_Producto}">Eliminar</button>
          </div>
        `;
        document.getElementById('productos-list').insertAdjacentHTML('beforeend', productoHtml);
        addEliminarEvento();
      } else {
        alert('Producto no encontrado');
      }
    })
    .catch(error => console.error('Error procesando la imagen: ', error));
  });
}
