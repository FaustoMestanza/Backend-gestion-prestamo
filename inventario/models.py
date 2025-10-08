# users/models.py
from django.db import models

class Equipo(models.Model):
    """
    Representa un equipo en el inventario institucional.
    """

    codigo = models.CharField(max_length=100, unique=True)   # Identificador único (usado para el QR)
    nombre = models.CharField(max_length=200)                # Nombre del equipo (por ej. 'Laptop Dell')
    categoria = models.CharField(max_length=100)             # Categoría general (Ej. 'Computadora', 'Proyector')
    descripcion = models.TextField(blank=True, null=True)    # Descripción opcional
    ubicacion = models.CharField(max_length=150, blank=True, null=True)  # Dónde se encuentra
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
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Se llena automáticamente al crear
    ultima_actualizacion = models.DateTimeField(auto_now=True) # Actualiza cada vez que se modifica
    qr_uuid = models.CharField(max_length=64, blank=True, null=True, unique=True)  # campo reservado para QR

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
