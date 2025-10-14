from django.db import models

class Equipo(models.Model):
    """
    Representa un equipo en el inventario institucional.
    """

    codigo = models.CharField(max_length=100, unique=True)  # Identificador único (usado para el QR)
    nombre = models.CharField(max_length=200, blank=True, null=True)  # opcional
    categoria = models.CharField(max_length=100, blank=True, null=True)  # opcional
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    estado = models.CharField(
        max_length=50,
        choices=[
            ("Disponible", "Disponible"),
            ("Prestado", "Prestado"),
            ("Mantenimiento", "Mantenimiento"),
            ("Dado de baja", "Dado de baja"),
        ],
        default="Disponible"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    qr_uuid = models.CharField(max_length=64, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.nombre or 'Sin nombre'} ({self.codigo})"

