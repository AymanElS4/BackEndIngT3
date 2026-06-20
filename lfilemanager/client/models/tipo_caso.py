from django.db import models


class TipoCaso(models.Model):
    """Modelo que define los distintos tipos de casos legales."""
    oid_tipo_caso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        """Metadatos del modelo TipoCaso."""
        db_table = 'tipo_caso'

    def __str__(self):
        """Devuelve la representación en cadena del tipo de caso."""
        return str(self.nombre)
