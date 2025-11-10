from django.contrib import admin
from .models import Prestamo

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ("id", "equipo_id", "usuario_id", "fecha_inicio", "fecha_compromiso", "estado", "registrado_por_id")
    list_filter = ("estado",)
    search_fields = ("equipo_id", "usuario_id")
