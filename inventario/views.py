from rest_framework import viewsets
from .models import Equipo
from .serializers import EquipoSerializer

class EquipoViewSet(viewsets.ModelViewSet):
    """
    Controlador REST que expone automáticamente los endpoints CRUD:
    GET, POST, PUT, PATCH, DELETE
    """
    queryset = Equipo.objects.all().order_by("-fecha_registro")
    serializer_class = EquipoSerializer
