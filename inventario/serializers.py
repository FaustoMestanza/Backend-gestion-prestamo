# users/serializers.py
from rest_framework import serializers
from .models import Equipo

class EquipoSerializer(serializers.ModelSerializer):
    """
    Serializador que transforma los datos del modelo Equipo a formato JSON
    
    """
    class Meta:
        model = Equipo
        fields = "__all__"  # incluye todos los campos del modelo
