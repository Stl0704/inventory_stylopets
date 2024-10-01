const video = document.getElementById('camera-stream');
const canvas = document.getElementById('camera-canvas');
const captureBtn = document.getElementById('capture-btn');
const stopCameraBtn = document.getElementById('stop-camera-btn');
let stream;

function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(mediaStream => {
      video.srcObject = mediaStream;
      stream = mediaStream;
    })
    .catch(error => {
      console.error('Error accediendo a la cámara: ', error);
    });
}

captureBtn.addEventListener('click', () => {
  if (!stream) {  // Solo accedemos a la cámara si no hay stream activo
    startCamera();
  }

  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageData = canvas.toDataURL('image/png');
  console.log('Imagen capturada', imageData);
});

// Evento para detener la cámara
stopCameraBtn.addEventListener('click', () => {
  if (stream) {
    const tracks = stream.getTracks(); // Obtener todos los tracks de video y audio
    tracks.forEach(track => track.stop()); // Detener cada uno de los tracks
    video.srcObject = null; // Eliminar el stream del elemento video
    stream = null; // Restablecer stream a null para permitir reiniciar la cámara
  }
});
