from django.db import models
from client.gas_storage import GASDriveStorage


def codigo_upload_path(instance, filename):
    return f'Códigos Legales/{instance.nombre_norma}/{filename}'

class CodigoLegal(models.Model):
    """Modelo que almacena normativas y códigos legales."""
    oid_codigo = models.AutoField(primary_key=True)
    nombre_norma = models.CharField(max_length=100, db_index=True)
    numero_articulo = models.CharField(max_length=50, db_index=True)
    texto_contenido = models.TextField()
    archivo_pdf = models.FileField(
        upload_to=codigo_upload_path, 
        storage=GASDriveStorage(), 
        null=True, 
        blank=True
    )
    vigencia = models.BooleanField(default=True, db_index=True)

    class Meta:
        """Metadatos del modelo CodigoLegal."""
        db_table = 'codigo_legal'
        ordering = ['nombre_norma', 'numero_articulo']
        unique_together = [('nombre_norma', 'numero_articulo')]

    def __str__(self):
        """Devuelve la representación en cadena del código legal."""
        return f"{self.nombre_norma} — Art. {self.numero_articulo}"
