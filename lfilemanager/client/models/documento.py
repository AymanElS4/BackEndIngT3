from django.db import models
from .caso import Caso
from client.gas_storage import GASDriveStorage


def documento_upload_path(instance, filename):
    try:
        tipo = instance.oid_caso.oid_tipo_caso.nombre
        estado = instance.oid_caso.oid_estado.nombre
    except AttributeError:
        tipo = 'Sin_Categoria'
        estado = 'Sin_Estado'
    return f'Casos Legales/{tipo}/{estado}/{filename}'

class Documento(models.Model):
    """Modelo que representa un documento adjunto a un caso."""
    oid_documento = models.AutoField(primary_key=True)
    oid_caso = models.ForeignKey(
        Caso, on_delete=models.CASCADE, db_column='oid_caso')
    nombre_archivo = models.CharField(max_length=150)
    ruta_archivo = models.FileField(
        upload_to=documento_upload_path,
        storage=GASDriveStorage()
    )
    tipo_documento = models.CharField(max_length=50)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo Documento."""
        db_table = 'documento'
        ordering = ['-fecha_subida']
