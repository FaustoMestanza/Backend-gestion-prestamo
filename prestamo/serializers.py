from rest_framework import serializers
from .models import Prestamo, EstadoPrestamo

class PrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestamo
        fields = ['id', 'equipo_id', 'usuario_id', 'fecha_inicio', 'fecha_compromiso', 'estado']

    def create(self, validated_data):
        # aseguramos que los IDs se pasen correctamente
        prestamo = Prestamo.objects.create(**validated_data)
        return prestamo
