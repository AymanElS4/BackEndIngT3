import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import Rol, Usuario, Caso, EstadoCaso, TipoCaso

pytestmark = pytest.mark.django_db


class TestCaseService:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse('caso-list')
        
        self.rol = Rol.objects.create(nombre='Abogado', descripcion='Abogado firma')
        self.lawyer_1 = Usuario.objects.create_user(email='lawyer1@x.com', password='pass', nombre='L1', oid_rol=self.rol)
        self.lawyer_2 = Usuario.objects.create_user(email='lawyer2@x.com', password='pass', nombre='L2', oid_rol=self.rol)
        
        self.estado_open = EstadoCaso.objects.create(nombre='OPEN')
        self.tipo = TipoCaso.objects.create(nombre='Civil', descripcion='Civil')
        
        # CORRECCIÓN: Nombres de atributos reales extraídos de caso.py y campos obligatorios
        Caso.objects.create(
            titulo="Caso Gonzales v. Banco", 
            oid_abogado=self.lawyer_1, 
            oid_estado=self.estado_open, 
            oid_tipo_caso=self.tipo,
            numero_expediente="EXP-2026-001",
            fecha_inicio=date(2026, 1, 1)
        )
        Caso.objects.create(
            titulo="Caso Gonzales Alimentos", 
            oid_abogado=self.lawyer_2, 
            oid_estado=self.estado_open, 
            oid_tipo_caso=self.tipo,
            numero_expediente="EXP-2026-002",
            fecha_inicio=date(2026, 1, 2)
        )

    def test_filter_cases_by_status_and_lawyer_returns_only_owned_cases(self):
        self.client.force_authenticate(user=self.lawyer_1)
        
        response = self.client.get(self.list_url, {'status': 'OPEN', 'search': 'Gonzales'})
        assert response.status_code == status.HTTP_200_OK
        
        resultados = response.json().get('results', response.json())
        assert len(resultados) == 1
        assert "Banco" in resultados[0]['titulo']

    def test_search_legal_case_by_keyword_shows_correct_case(self):
        self.client.force_authenticate(user=self.lawyer_1)
        
        response = self.client.get(self.list_url, {'search': 'Gonzales'})
        assert response.status_code == status.HTTP_200_OK
        
        resultados = response.json().get('results', response.json())
        assert len(resultados) == 1