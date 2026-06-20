import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from client.models import Rol, Usuario, Notificacion

pytestmark = pytest.mark.django_db


class TestNotificationApi:

    @pytest.fixture(autouse=True)
    def setup_method_fixtures(self, db):
        self.client = APIClient()
        self.list_url = reverse('notificacion-list')
        
        self.admin_role = Rol.objects.create(nombre='Administrador', descripcion='Admin del sistema')
        self.user_role = Rol.objects.create(nombre='Profesional', descripcion='Usuario profesional')

    @pytest.fixture
    def sample_users(self):
        admin = Usuario.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            nombre='Admin Test',
            oid_rol=self.admin_role,
            is_staff=True,
            is_superuser=True
        )
        regular = Usuario.objects.create_user(
            email='user@example.com',
            password='userpass123',
            nombre='User Test',
            oid_rol=self.user_role
        )
        other = Usuario.objects.create_user(
            email='other@example.com',
            password='otherpass123',
            nombre='Other Test',
            oid_rol=self.user_role
        )
        return {'admin': admin, 'regular': regular, 'other': other}

    @pytest.fixture
    def setup_notifications(self, sample_users):
        notif_regular = Notificacion.objects.create(
            oid_usuario=sample_users['regular'],
            titulo='Aviso para usuario',
            mensaje='Mensaje de prueba para el usuario regular.',
            tipo='in-app'
        )
        notif_other = Notificacion.objects.create(
            oid_usuario=sample_users['other'],
            titulo='Aviso para otro',
            mensaje='Mensaje de prueba para un usuario distinto.',
            tipo='in-app'
        )
        return {'regular_notif': notif_regular, 'other_notif': notif_other}

    def _extract_results(self, response):
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_non_admin_only_sees_own_notifications(self, sample_users, setup_notifications):
        self.client.force_authenticate(user=sample_users['regular'])
        
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        
        items = self._extract_results(response)
        retrieved_ids = {item['oid_notificacion'] for item in items}
        
        assert setup_notifications['regular_notif'].oid_notificacion in retrieved_ids
        assert setup_notifications['other_notif'].oid_notificacion not in retrieved_ids

    def test_admin_creates_global_notification(self, sample_users):
        self.client.force_authenticate(user=sample_users['admin'])
        
        payload = {
            'titulo': 'Notificación global de admin',
            'mensaje': 'Mensaje global creado por administrador desde API.',
            'tipo': 'in-app'
        }
        
        response = self.client.post(self.list_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        assert response_data.get('oid_usuario') in (None, '')
        assert response_data['titulo'] == payload['titulo']