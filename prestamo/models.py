from django.db import models

class EstadoPrestamo(models.TextChoices):
    ABIERTO = "Abierto", "Abierto"
    CERRADO = "Cerrado", "Cerrado"
    VENCIDO = "Vencido", "Vencido"

class Prestamo(models.Model):
    equipo_id = models.IntegerField()   # ID del equipo (de Inventario)
    usuario_id = models.IntegerField()  # ID del usuario (de Usuarios)
    registrado_por_id = models.IntegerField(null=True, blank=True)


    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_compromiso = models.DateTimeField()
    estado = models.CharField(
        max_length=20,
        choices=EstadoPrestamo.choices,
        default=EstadoPrestamo.ABIERTO
    
    )

    def __str__(self):
        return f"Préstamo {self.id} - Equipo {self.equipo_id}"
