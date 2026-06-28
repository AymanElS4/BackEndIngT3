"""Module-level docstring for the caso_normativa model."""
from django.db import models

from .caso import Caso
from .codigo_legal import CodigoLegal


class CasoNormativa(models.Model):
    """Modelo intermedio para la relación entre un caso y una normativa."""

    oid_relacion = models.AutoField(primary_key=True)
    oid_caso = models.ForeignKey(
        Caso,
        on_delete=models.CASCADE,
        db_column='oid_caso'
    )
    oid_codigo = models.ForeignKey(
        CodigoLegal,
        on_delete=models.CASCADE,
        db_column='oid_codigo'
    )
    fecha_asociacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo CasoNormativa."""

        db_table = 'caso_normativa'
        unique_together = ('oid_caso', 'oid_codigo')
