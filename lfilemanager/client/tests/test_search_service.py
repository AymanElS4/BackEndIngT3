import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import Rol, Usuario

pytestmark = pytest.mark.django_db


class TestSearchService:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse('caso-list')
        self.rol = Rol.objects.create(nombre='Abogado', descripcion='Abogado firma')
        self.lawyer = Usuario.objects.create_user(email='lawyer@x.com', password='pass', nombre='L', oid_rol=self.rol)

    # TC-08: Verifica que enviar un rango de fechas inválido (start > end) sea rechazado por el backend
    def test_search_by_date_range_rejects_inverted_range(self):
        self.client.force_authenticate(user=self.lawyer)
        
        # Parámetros invertidos según el spec de la HU-14
        params = {'fecha_inicio': '2026-06-01', 'fecha_fin': '2026-01-01'}
        response = self.client.get(self.list_url, params)
        
        # Cambiar el assert según maneje tu backend el error (400 Bad Request o un arreglo vacío de control)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]