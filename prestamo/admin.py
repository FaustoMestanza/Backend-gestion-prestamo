# users/admin.py
from django.contrib import admin
from .models import Prestamo

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_id', 'equipo_id', 'fecha_inicio', 'fecha_compromiso', 'estado')
    readonly_fields = ('id',)