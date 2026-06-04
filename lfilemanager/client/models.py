"""
Modelos del dominio legal — Esquema estricto según contexto.md
Inheriting from AbstractBaseUser for proper DRF/JWT integration.
"""
# pylint: disable=too-few-public-methods,import-error

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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

class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un usuario con el email y contraseña dados."""
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y guarda un superusuario con el email y contraseña dados."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Ensure a role exists for superuser
        rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
        extra_fields.setdefault('oid_rol', rol_admin)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo que representa a un usuario del sistema (abogados, admins, etc.)."""
    oid_usuario = models.AutoField(primary_key=True)
    oid_rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        db_column='oid_rol',
        related_name='usuarios',
        null=True
    )
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    matricula_profesional = models.CharField(max_length=50, blank=True, default='')
    especialidad = models.CharField(max_length=100, blank=True, default='')
    telefono_contacto = models.CharField(max_length=20, blank=True, default='')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        """Metadatos del modelo Usuario."""
        db_table = 'usuario'

    def __str__(self):
        """Devuelve la representación en cadena del usuario."""
        return f"{self.nombre} ({self.email})"

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

class CodigoLegal(models.Model):
    """Modelo que almacena normativas y códigos legales."""
    oid_codigo = models.AutoField(primary_key=True)
    nombre_norma = models.CharField(max_length=100, db_index=True)
    numero_articulo = models.CharField(max_length=50, db_index=True)
    texto_contenido = models.TextField()
    vigencia = models.BooleanField(default=True, db_index=True)

    class Meta:
        """Metadatos del modelo CodigoLegal."""
        db_table = 'codigo_legal'
        ordering = ['nombre_norma', 'numero_articulo']
        unique_together = [('nombre_norma', 'numero_articulo')]

    def __str__(self):
        """Devuelve la representación en cadena del código legal."""
        return f"{self.nombre_norma} — Art. {self.numero_articulo}"

class CasoNormativa(models.Model):
    """Modelo intermedio para la relación entre un caso y una normativa."""
    oid_relacion = models.AutoField(primary_key=True)
    oid_caso = models.ForeignKey(Caso, on_delete=models.CASCADE, db_column='oid_caso')
    oid_codigo = models.ForeignKey(CodigoLegal, on_delete=models.CASCADE, db_column='oid_codigo')
    fecha_asociacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo CasoNormativa."""
        db_table = 'caso_normativa'
        unique_together = ('oid_caso', 'oid_codigo')

class Documento(models.Model):
    """Modelo que representa un documento adjunto a un caso."""
    oid_documento = models.AutoField(primary_key=True)
    oid_caso = models.ForeignKey(Caso, on_delete=models.CASCADE, db_column='oid_caso')
    nombre_archivo = models.CharField(max_length=150)
    ruta_archivo = models.FileField(upload_to='documentos/%Y/%m/')
    tipo_documento = models.CharField(max_length=50)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo Documento."""
        db_table = 'documento'
        ordering = ['-fecha_subida']

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

class Pago(models.Model):
    """Modelo que registra los pagos realizados por los usuarios."""
    oid_pago = models.AutoField(primary_key=True)
    oid_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='oid_usuario')
    oid_plan = models.ForeignKey(Plan, on_delete=models.PROTECT, db_column='oid_plan')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
    estado_pago = models.CharField(max_length=20) # Ej: Pendiente, Completado, Fallido
    referencia_externa = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        """Metadatos del modelo Pago."""
        db_table = 'pago'

    def __str__(self):
        """Devuelve la representación en cadena del pago."""
        return f"Pago {self.oid_pago} - {self.oid_usuario.email}"

class Notificacion(models.Model):
    """Modelo que gestiona las notificaciones enviadas a los usuarios."""
    oid_notificacion = models.AutoField(primary_key=True)
    oid_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='oid_usuario')
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=30) # Ej: in-app, email
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo Notificacion."""
        db_table = 'notificacion'
        ordering = ['-fecha_creacion']

    def __str__(self):
        """Devuelve la representación en cadena de la notificación."""
        return f"{self.titulo} - {self.oid_usuario.email}"
