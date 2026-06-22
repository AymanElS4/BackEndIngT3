import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import (
    Rol, Usuario, Caso, EstadoCaso, TipoCaso, CodigoLegal, CasoNormativa
)

pytestmark = pytest.mark.django_db


class TestCasoNormativaService:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse('caso-normativa-list')

        self.rol_abogado = Rol.objects.create(nombre='Abogado', descripcion='Abogado firma')
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Admin')

        self.lawyer_1 = Usuario.objects.create_user(
            email='lawyer1@x.com', password='pass', nombre='L1', oid_rol=self.rol_abogado
        )
        self.lawyer_2 = Usuario.objects.create_user(
            email='lawyer2@x.com', password='pass', nombre='L2', oid_rol=self.rol_abogado
        )
        self.admin = Usuario.objects.create_user(
            email='admin@x.com', password='pass', nombre='Admin', oid_rol=self.rol_admin
        )

        self.estado = EstadoCaso.objects.create(nombre='Activo')
        self.tipo = TipoCaso.objects.create(nombre='Civil', descripcion='Civil')

        self.caso_lawyer_1 = Caso.objects.create(
            titulo='Caso del Abogado 1',
            oid_abogado=self.lawyer_1,
            oid_estado=self.estado,
            oid_tipo_caso=self.tipo,
            numero_expediente='EXP-2026-001',
            fecha_inicio=date(2026, 1, 1)
        )
        self.caso_lawyer_2 = Caso.objects.create(
            titulo='Caso del Abogado 2',
            oid_abogado=self.lawyer_2,
            oid_estado=self.estado,
            oid_tipo_caso=self.tipo,
            numero_expediente='EXP-2026-002',
            fecha_inicio=date(2026, 1, 2)
        )

        self.articulo = CodigoLegal.objects.create(
            nombre_norma='Código Civil',
            numero_articulo='Art. 1750',
            texto_contenido='Obligaciones del arrendatario...',
            vigencia=True
        )
        self.articulo_2 = CodigoLegal.objects.create(
            nombre_norma='Código Penal',
            numero_articulo='Art. 45',
            texto_contenido='Infracciones...',
            vigencia=True
        )

    def test_associate_article_to_case_creates_reference(self):
        self.client.force_authenticate(user=self.lawyer_1)

        response = self.client.post(self.list_url, {
            'oid_caso': self.caso_lawyer_1.oid_caso,
            'oid_codigo': self.articulo.oid_codigo
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['codigo_numero_articulo'] == 'Art. 1750'
        assert CasoNormativa.objects.filter(
            oid_caso=self.caso_lawyer_1, oid_codigo=self.articulo
        ).exists()

    def test_list_references_returns_only_articles_of_requested_case(self):
        CasoNormativa.objects.create(oid_caso=self.caso_lawyer_1, oid_codigo=self.articulo)
        CasoNormativa.objects.create(oid_caso=self.caso_lawyer_1, oid_codigo=self.articulo_2)
        self.client.force_authenticate(user=self.lawyer_1)

        response = self.client.get(self.list_url, {'oid_caso': self.caso_lawyer_1.oid_caso})

        assert response.status_code == status.HTTP_200_OK
        resultados = response.json().get('results', response.json())
        assert len(resultados) == 2

    def test_associate_duplicate_article_returns_validation_error(self):
        CasoNormativa.objects.create(oid_caso=self.caso_lawyer_1, oid_codigo=self.articulo)
        self.client.force_authenticate(user=self.lawyer_1)

        response = self.client.post(self.list_url, {
            'oid_caso': self.caso_lawyer_1.oid_caso,
            'oid_codigo': self.articulo.oid_codigo
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unlink_article_removes_reference(self):
        relacion = CasoNormativa.objects.create(
            oid_caso=self.caso_lawyer_1, oid_codigo=self.articulo
        )
        self.client.force_authenticate(user=self.lawyer_1)
        detail_url = reverse('caso-normativa-detail', args=[relacion.oid_relacion])

        response = self.client.delete(detail_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CasoNormativa.objects.filter(oid_relacion=relacion.oid_relacion).exists()

    def test_lawyer_cannot_associate_article_to_foreign_case(self):
        self.client.force_authenticate(user=self.lawyer_1)

        response = self.client.post(self.list_url, {
            'oid_caso': self.caso_lawyer_2.oid_caso,
            'oid_codigo': self.articulo.oid_codigo
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not CasoNormativa.objects.filter(oid_caso=self.caso_lawyer_2).exists()

    def test_lawyer_does_not_see_references_of_foreign_case(self):
        CasoNormativa.objects.create(oid_caso=self.caso_lawyer_2, oid_codigo=self.articulo)
        self.client.force_authenticate(user=self.lawyer_1)

        response = self.client.get(self.list_url, {'oid_caso': self.caso_lawyer_2.oid_caso})

        assert response.status_code == status.HTTP_200_OK
        resultados = response.json().get('results', response.json())
        assert len(resultados) == 0

    def test_admin_can_associate_article_to_any_case(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(self.list_url, {
            'oid_caso': self.caso_lawyer_1.oid_caso,
            'oid_codigo': self.articulo.oid_codigo
        })

        assert response.status_code == status.HTTP_201_CREATED
