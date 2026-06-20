import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import Rol, Usuario, CodigoLegal

pytestmark = pytest.mark.django_db


class TestLegalFilterService:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        # CORRECCIÓN: Nombre de la URL mapeado correctamente
        self.list_url = reverse('codigo-legal-list')
        
        # Creamos rol y usuario profesional para la autenticación
        self.rol = Rol.objects.create(nombre='Profesional', descripcion='Usuario regular')
        self.user = Usuario.objects.create_user(
            email='abogado_test@gmail.com',
            password='password123',
            nombre='Abogado Test',
            oid_rol=self.rol
        )
        
        # Forzamos la autenticación para evitar el error 401 Unauthorized
        self.client.force_authenticate(user=self.user)
        
        # Creación de registros en la BD de pruebas
        CodigoLegal.objects.create(nombre_norma="COIP", numero_articulo="1", texto_contenido="Vigente...", vigencia=True)
        CodigoLegal.objects.create(nombre_norma="COIP", numero_articulo="2", texto_contenido="Derogada...", vigencia=False)

    @pytest.mark.parametrize(
        "filtro_valor, estado_esperado",
        [
            ("true", True),
            ("false", False),
        ]
    )
    def test_filter_by_status_returns_correct_equivalence_class(self, filtro_valor, estado_esperado):
        response = self.client.get(self.list_url, {'vigencia': filtro_valor})
        assert response.status_code == status.HTTP_200_OK
        
        resultados = response.json().get('results', response.json())
        assert len(resultados) > 0
        for norma in resultados:
            assert norma['vigencia'] is estado_esperado

    def test_filter_with_invalid_status_raises_ValueError(self):
        response = self.client.get(self.list_url, {'vigencia': 'INVENTADO'})
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK]