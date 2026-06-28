"""Module for the Rol model representing user roles in the system."""
from django.db import models


class Rol(models.Model):
    """Modelo que representa los roles de los usuarios en el sistema."""
    oid_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        """Metadatos del modelo Rol."""
        db_table = 'rol'

    def __str__(self):
        """Devuelve la representación en cadena del rol."""
        return str(self.nombre)
