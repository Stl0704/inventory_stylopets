from django.db import models

class ProductoTests(models.Model):
    Id_Producto = models.AutoField(primary_key=True)  # Llave primaria automática
    SKU = models.CharField(max_length=100, unique=True)  # Campo único para SKU
    Nombre = models.CharField(max_length=255)  # Nombre del producto
    Categoria = models.CharField(max_length=100)  # Categoría del producto
    Stock = models.IntegerField()  # Stock del producto

    def __str__(self):
        return f"{self.Nombre} - {self.SKU}"

    class Meta:
        verbose_name_plural = "Producto Tests"

class IngresoTest(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=255)

    def __str__(self):
        return f"Ingreso {self.id_ingreso} - {self.fecha}"

class HistorialIngresosTests(models.Model):
    Id_Ingreso = models.OneToOneField(IngresoTest, on_delete=models.CASCADE, primary_key=True)  # Relación con IngresoTest
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=100)  # Persona responsable del ingreso

    def __str__(self):
        return f"Ingreso {self.Id_Ingreso.id_ingreso} - Responsable: {self.responsable} - Fecha: {self.fecha}"
    
    
class DetalleIngresoTest(models.Model):
    ingreso = models.ForeignKey(IngresoTest, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(ProductoTests, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"Detalle de Ingreso {self.ingreso.id_ingreso} - Producto: {self.producto.Nombre}"

