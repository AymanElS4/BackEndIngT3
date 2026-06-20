from django.db import models
from .usuario import Usuario
from .tipo_caso import TipoCaso
from .estado_caso import EstadoCaso


class Caso(models.Model):
    """Modelo principal que representa un caso o expediente legal."""
    oid_caso = models.AutoField(primary_key=True)
    oid_abogado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='oid_abogado',
        related_name='casos'
    )
    oid_tipo_caso = models.ForeignKey(
        TipoCaso,
        on_delete=models.PROTECT,
        db_column='oid_tipo_caso',
        related_name='casos'
    )
    oid_estado = models.ForeignKey(
        EstadoCaso,
        on_delete=models.PROTECT,
        db_column='oid_estado',
        related_name='casos'
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')
    numero_expediente = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField(null=True, blank=True)
    juzgado = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        """Metadatos del modelo Caso."""
        db_table = 'caso'
        ordering = ['-fecha_inicio']

    def __str__(self):
        """Devuelve la representación en cadena del caso."""
        return f"{self.numero_expediente} — {self.titulo}"
