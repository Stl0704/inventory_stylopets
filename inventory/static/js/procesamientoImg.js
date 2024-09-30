const video = document.getElementById('camera-stream');
const canvas = document.getElementById('camera-canvas');
const captureBtn = document.getElementById('capture-btn');

// Acceder a la cámara
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(error => {
    console.error('Error accediendo a la cámara: ', error);
  });

// Capturar el código de barras o QR
captureBtn.addEventListener('click', () => {
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Aquí puedes procesar la imagen del canvas para obtener el código QR o de barras
  const imageData = canvas.toDataURL('image/png');
  console.log('Imagen capturada', imageData);  // Enviar esta imagen al backend si es necesario
});
