from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Prestamo, EstadoPrestamo
from .serializers import PrestamoSerializer
import requests

# 🌐 URLs de tus microservicios en la nube (Azure)
USUARIOS_URL = "https://microservicio-usuarios-gsbhdjavc9fjf9a8.brazilsouth-01.azurewebsites.net/api/v1/usuarios/"

INVENTARIO_URL = "https://microservicio-gestioninventario-e7byadgfgdhpfyen.brazilsouth-01.azurewebsites.net/api/equipos/"

class PrestamoViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para gestión de préstamos
    """
    queryset = Prestamo.objects.all().order_by('-fecha_inicio')
    serializer_class = PrestamoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        usuario_id = data.get("usuario_id")
        equipo_id = data.get("equipo_id")

        #  Validar usuario desde microservicio Usuarios
        try:
            user_response = requests.get(f"{USUARIOS_URL}{usuario_id}/")
            if user_response.status_code != 200:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException:
            return Response({"error": "Error de conexión con microservicio de usuarios"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        #  Validar equipo desde microservicio Inventario
        try:
            eq_response = requests.get(f"{INVENTARIO_URL}{equipo_id}/")
            if eq_response.status_code != 200:
                return Response({"error": "Equipo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            equipo = eq_response.json()
            if equipo.get("estado") != "Disponible":
                return Response({"error": "Equipo no disponible para préstamo"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException:
            return Response({"error": "Error de conexión con microservicio de inventario"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        #  Crear el préstamo
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        prestamo = serializer.save(estado=EstadoPrestamo.ABIERTO)

        #  Cambiar estado del equipo a “Prestado”
        try:
            patch_resp = requests.patch(f"{INVENTARIO_URL}{equipo_id}/", json={"estado": "Prestado"})
            print("PATCH inventario:", patch_resp.status_code, patch_resp.text)
        except requests.exceptions.RequestException as e:
            print(" Error actualizando estado del equipo:", e)
            pass  # no detiene el flujo si no responde

        return Response(
            {
                "mensaje": "Préstamo registrado correctamente",
                "prestamo": PrestamoSerializer(prestamo).data
            },
            status=status.HTTP_201_CREATED
        )
