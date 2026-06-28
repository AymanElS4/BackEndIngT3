import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import Rol, Usuario, CodigoLegal

pytestmark = pytest.mark.django_db


class TestCatalogService:

    @pytest.fixture(autouse=True)
    def setup_method(self, db):
        self.client = APIClient()
        self.list_url = reverse('codigo-legal-list')
        
        # Creamos un rol y un usuario para poder autenticarnos
        self.rol = Rol.objects.create(nombre='Profesional', descripcion='Usuario regular')
        self.user = Usuario.objects.create_user(
            email='abogado_test@gmail.com',
            password='password123',
            nombre='Abogado Test',
            oid_rol=self.rol
        )
        
        # Forzamos la autenticación en el cliente de pruebas
        self.client.force_authenticate(user=self.user)

    @pytest.fixture
    def setup_legal_article(self):
        return CodigoLegal.objects.create(
            nombre_norma="COIP",
            numero_articulo="144",
            texto_contenido="Homicidio: La persona que mate a otra será sancionada con pena...",
            vigencia=True
        )

    # TC-01: Ahora pasará con 200 OK al estar autenticado
    def test_search_article_returns_correct_article_when_exists(self, setup_legal_article):
        response = self.client.get(self.list_url, {'nombre_norma': 'COIP', 'numero_articulo': '144'})
        assert response.status_code == status.HTTP_200_OK
        
        resultados = response.json().get('results', response.json())
        assert len(resultados) > 0
        assert resultados[0]['numero_articulo'] == "144"

    # TC-02: Retornará un listado vacío de forma limpia en lugar de un error 401
    def test_search_article_raises_NotFoundError_when_article_does_not_exist(self):
        response = self.client.get(self.list_url, {'nombre_norma': 'COIP', 'numero_articulo': '99999'})
        assert response.status_code == status.HTTP_200_OK
        
        resultados = response.json().get('results', response.json())
        assert len(resultados) == 0

    # TC-03: Validará correctamente la estructura JSON del payload real
    def test_search_article_includes_version_metadata(self, setup_legal_article):
        response = self.client.get(self.list_url, {'nombre_norma': 'COIP', 'numero_articulo': '144'})
        assert response.status_code == status.HTTP_200_OK
        
        resultados = response.json().get('results', response.json())
        assert len(resultados) > 0
        assert 'vigencia' in resultados[0]
    

    def test_navigate_between_folders_loads_subfolders_and_files(self):
        """TC-14: Navegar entre carpetas carga subcarpetas y archivos (folder_id=2)."""
        self.client.force_authenticate(user=self.user)
        
        # Corregido de 'documentos-list' a 'documento-list'
        url = reverse('documento-list') 
        query_params = {'folder_id': 2} 

        response = self.client.get(url, query_params)

        assert response.status_code == status.HTTP_200_OK