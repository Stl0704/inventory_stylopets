// escanerCamara.js

// Obtener referencias a los elementos del DOM
const video = document.getElementById('camera-stream');
const canvas = document.getElementById('camera-canvas');
const context = canvas.getContext('2d');
const captureBtn = document.getElementById('capture-btn');
const obtenerBtn = document.getElementById('obtener-btn');
const stopCameraBtn = document.getElementById('stop-camera-btn');
let stream = null;
let imageDataURL = null; // Variable para almacenar la imagen capturada

console.log('escanerCamara.js cargado correctamente.');
// Función para iniciar la cámara
function startCamera() {
    console.log('Intentando iniciar la cámara...');
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(mediaStream => {
            video.srcObject = mediaStream;
            stream = mediaStream;
            video.play();
            console.log('Cámara iniciada correctamente.');
        })
        .catch(error => {
            console.error('Error accediendo a la cámara:', error);
            alert('No se pudo acceder a la cámara. Por favor, revisa los permisos.');
        });
}

// Función para capturar la imagen
function captureImage() {
    console.log('Capturando imagen...');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    imageDataURL = canvas.toDataURL('image/png');
    console.log('Imagen capturada:', imageDataURL.substring(0, 50) + '...'); // Mostrar solo los primeros 50 caracteres

    if (imageDataURL && imageDataURL.startsWith('data:image/png')) {
        console.log('Imagen capturada correctamente.');
        // Mostrar el botón "Obtener"
        obtenerBtn.style.display = 'inline-block';
        console.log('Botón "Obtener" mostrado.');
    } else {
        console.log('Error al capturar la imagen.');
        alert('Error al capturar la imagen.');
    }
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

// Evento para el botón "Escanear"
captureBtn.addEventListener('click', () => {
    console.log('Botón "Escanear" clicado.');

    if (!stream) {  // Solo iniciamos la cámara si no está activa
        console.log('No hay stream activo. Iniciando cámara...');
        startCamera();
    }

    // Esperar a que el video esté listo
    if (video.readyState >= 2) { // HAVE_CURRENT_DATA
        console.log('Video listo para capturar.');
        captureImage();
    } else {
        console.log('Video no está listo, esperando...');
        video.addEventListener('loadeddata', captureImage, { once: true });
    }
});

// Evento para el botón "Obtener"
obtenerBtn.addEventListener('click', () => {
    console.log('Botón "Obtener" clicado.');

    if (!imageDataURL) {
        console.log('No hay una imagen capturada para procesar.');
        alert('No hay una imagen capturada para procesar.');
        return;
    }

    // Crear un objeto Image para cargar la imagen capturada
    const img = new Image();
    img.src = imageDataURL;
    img.onload = () => {
        console.log('Imagen cargada para escanear.');

        // Crear un canvas temporal para obtener ImageData
        const tempCanvas = document.createElement('canvas');
        const tempContext = tempCanvas.getContext('2d');
        tempCanvas.width = img.width;
        tempCanvas.height = img.height;
        tempContext.drawImage(img, 0, 0, img.width, img.height);
        const tempImageData = tempContext.getImageData(0, 0, img.width, img.height);

        // Usar jsQR para detectar códigos
        console.log('Intentando detectar QR...');
        const code = jsQR(tempImageData.data, tempImageData.width, tempImageData.height);

        if (code) {
            console.log('Código detectado:', code.data);
            alert(`Código detectado: ${code.data}`);

            // Enviar el código al backend para procesarlo
            fetch('/inventory/obtener-scan/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ codigo: code.data })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Respuesta del servidor:', data);
                if (data.producto) {
                    alert(`Producto encontrado: ${data.producto.Nombre}`);
                    // Añadir el producto al carrito
                    productos.push(data.producto);
                    actualizarListaProductos();
                    console.log(`Producto ${data.producto.Nombre} añadido al carrito.`);
                } else if (data.error) {
                    alert(`Error: ${data.error}`);
                    console.log(`Error del servidor: ${data.error}`);
                } else {
                    alert('Respuesta inesperada del servidor.');
                    console.log('Respuesta inesperada del servidor:', data);
                }
            })
            .catch(error => {
                console.error('Error al procesar el código:', error);
                alert('Hubo un problema al procesar el código.');
            });

        } else {
            console.log('No se detectó ningún código.');
        }
    };

    img.onerror = () => {
        console.log('Error al cargar la imagen para escanear.');
        alert('Error al cargar la imagen para escanear.');
    };
});

// Evento para detener la cámara
stopCameraBtn.addEventListener('click', () => {
    console.log('Botón "Cerrar Escáner" clicado.');
    if (stream) {
        const tracks = stream.getTracks(); // Obtener todos los tracks de video y audio
        tracks.forEach(track => track.stop()); // Detener cada uno de los tracks
        video.srcObject = null; // Eliminar el stream del elemento video
        stream = null; // Restablecer stream a null para permitir reiniciar la cámara
        imageDataURL = null; // Limpiar la imagen capturada
        productos = []; // Limpiar el carrito
        actualizarListaProductos(); // Actualizar la interfaz
        console.log('Cámara detenida y stream limpiado.');
    }

    // Ocultar el botón "Obtener"
    obtenerBtn.style.display = 'none';
    console.log('Botón "Obtener" ocultado.');
});

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
