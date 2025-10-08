# users/admin.py
from django.contrib import admin
from .models import Equipo

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "estado", "ubicacion", "fecha_registro")
    search_fields = ("codigo", "nombre", "categoria", "ubicacion")
    list_filter = ("estado", "categoria")
