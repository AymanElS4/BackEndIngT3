"""Module for the Notificacion model."""
from django.db import models

from .usuario import Usuario


class Notificacion(models.Model):
    """Modelo que gestiona las notificaciones enviadas a los usuarios."""

    oid_notificacion = models.AutoField(primary_key=True)
    oid_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='oid_usuario',
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=30, default='in-app')
    # Ej: in-app, email
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo Notificacion."""

        db_table = 'notificacion'
        ordering = ['-fecha_creacion']

    def __str__(self):
        """Devuelve la representación en cadena de la notificación."""
        usuario_email = getattr(self.oid_usuario, 'email', None)
        usuario_display = usuario_email if usuario_email else 'Sistema'
        return f"{self.titulo} - {usuario_display}"
