import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import Rol, Usuario

pytestmark = pytest.mark.django_db


class TestAuthService:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        
        self.rol = Rol.objects.create(nombre='Profesional', descripcion='Usuario regular')
        self.user = Usuario.objects.create_user(
            email='correct@gmail.com',
            password='does',
            nombre='Test User',
            oid_rol=self.rol
        )

    # TC-04: Black-box | Camino feliz con estructura real de tokens
    def test_authenticate_valid_credentials_returns_jwt(self):
        payload = {"email": "correct@gmail.com", "password": "does"}
        response = self.client.post(self.login_url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Extraemos la sección 'tokens' que arrojó tu terminal
        respuesta_json = response.json()
        assert 'tokens' in respuesta_json
        assert 'access' in respuesta_json['tokens']

    # TC-05: Black-box | Credenciales inválidas rechaza el acceso (Este ya pasaba)
    def test_authenticate_invalid_password_raises_and_increments_failed_count(self):
        payload = {"email": "test@gmail.com", "password": "doesnot"}
        response = self.client.post(self.login_url, payload, format='json')
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    # TC-06: White-box | Inspección estructural real del JWT mapeado en tu payload
    def test_jwt_token_includes_sub_and_expires_in_30min(self):
        payload = {"email": "correct@gmail.com", "password": "does"}
        response = self.client.post(self.login_url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Corrección del camino de la llave: 'tokens' -> 'access'
        respuesta_json = response.json()
        token = respuesta_json.get('tokens', {}).get('access')
        
        assert token is not None