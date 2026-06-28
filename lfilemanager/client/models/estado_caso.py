"""Module for the EstadoCaso model defining possible legal case statuses."""
from django.db import models


class EstadoCaso(models.Model):
    """Modelo que define los posibles estados de un caso legal."""
    oid_estado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        """Metadatos del modelo EstadoCaso."""
        db_table = 'estado_caso'

    def __str__(self):
        """Devuelve la representación en cadena del estado del caso."""
        return str(self.nombre)
