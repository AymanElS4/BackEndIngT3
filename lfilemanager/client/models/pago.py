"""Module for the Pago model recording user payments."""
from django.db import models
from .usuario import Usuario
from .plan import Plan


class Pago(models.Model):
    """Modelo que registra los pagos realizados por los usuarios."""
    oid_pago = models.AutoField(primary_key=True)
    oid_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column='oid_usuario')
    oid_plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, db_column='oid_plan')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
    estado_pago = models.CharField(max_length=20)
    # Ej: Pendiente, Completado, Fallido
    referencia_externa = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        """Metadatos del modelo Pago."""
        db_table = 'pago'

    def __str__(self):
        """Devuelve la representación en cadena del pago."""
        usuario_email = getattr(self.oid_usuario, 'email', None)
        usuario_display = usuario_email if usuario_email else 'Usuario desconocido'
        return f"Pago {self.oid_pago} - {usuario_display}"
