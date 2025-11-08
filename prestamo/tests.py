from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


class MigrationTests(TestCase):
    def test_migrations_applied(self):
        """
        Verifica que las migraciones se aplican correctamente sin errores.
        """
        try:
            call_command("migrate", "--check")
            ok = True
        except Exception as e:
            ok = False
            print(f"Error en migraciones: {e}")
        self.assertTrue(ok, " Hay migraciones pendientes o con errores")


class UserAndAuthTests(TestCase):
    def setUp(self):
        # Cliente para simular peticiones
        self.client = APIClient()

        # Crear un rol
        

        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            rol=self.rol_admin
        )

    def test_usuario_con_rol(self):
        """Verifica que el usuario tenga rol asignado"""
        self.assertEqual(self.user.rol.nombre, "ADMIN")

    def test_login_endpoint(self):
        """Verifica que el login devuelve un token JWT"""
        response = self.client.post("/api/v1/auth/login/", {
            "username": "testuser",
            "password": "testpassword123"
        }, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_endpoint(self):
        """Verifica que /me/ devuelve info del usuario autenticado"""
        # Primero loguearse
        login_res = self.client.post("/api/v1/auth/login/", {
            "username": "testuser",
            "password": "testpassword123"
        }, format="json")

        token = login_res.data["access"]

        # Acceder a /me/ con token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")
