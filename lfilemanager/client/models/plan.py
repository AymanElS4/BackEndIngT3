"""Module for the Plan model defining available subscription plans."""
from django.db import models


class Plan(models.Model):
    """Modelo que define los planes de suscripción disponibles."""
    oid_plan = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anual = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, default='')
    estado = models.BooleanField(default=True)

    class Meta:
        """Metadatos del modelo Plan."""
        db_table = 'plan'

    def __str__(self):
        """Devuelve la representación en cadena del plan."""
        return str(self.nombre)
