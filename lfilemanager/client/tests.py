from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Rol, Usuario, Notificacion


class NotificacionApiTests(APITestCase):
    def setUp(self):
        self.admin_role = Rol.objects.create(nombre='Administrador', descripcion='Admin del sistema')
        self.user_role = Rol.objects.create(nombre='Profesional', descripcion='Usuario profesional')

        self.admin_user = Usuario.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            nombre='Admin Test',
            oid_rol=self.admin_role,
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = Usuario.objects.create_user(
            email='user@example.com',
            password='userpass123',
            nombre='User Test',
            oid_rol=self.user_role
        )

        self.other_user = Usuario.objects.create_user(
            email='other@example.com',
            password='otherpass123',
            nombre='Other Test',
            oid_rol=self.user_role
        )

        self.notification_of_regular = Notificacion.objects.create(
            oid_usuario=self.regular_user,
            titulo='Aviso para usuario',
            mensaje='Mensaje de prueba para el usuario regular.',
            tipo='in-app'
        )

        self.notification_of_other = Notificacion.objects.create(
            oid_usuario=self.other_user,
            titulo='Aviso para otro',
            mensaje='Mensaje de prueba para un usuario distinto.',
            tipo='in-app'
        )

        self.client = APIClient()
        self.list_url = reverse('notificacion-list')

    def _extract_results(self, response):
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_non_admin_only_sees_own_notifications(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_items = self._extract_results(response)
        response_ids = {item['oid_notificacion'] for item in response_items}
        self.assertIn(self.notification_of_regular.oid_notificacion, response_ids)
        self.assertNotIn(self.notification_of_other.oid_notificacion, response_ids)

    def test_admin_creates_global_notification(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'titulo': 'Notificación global de admin',
            'mensaje': 'Mensaje global creado por administrador desde API.',
            'tipo': 'in-app'
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Admin-created notifications are global (oid_usuario is null)
        self.assertTrue(response.json().get('oid_usuario') in (None, ''))
        self.assertEqual(response.json()['titulo'], payload['titulo'])
