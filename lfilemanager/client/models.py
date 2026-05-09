"""
Modelos del dominio legal — Esquema estricto según contexto.md
Inheriting from AbstractBaseUser for proper DRF/JWT integration.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Rol(models.Model):
    oid_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'rol'
    def __str__(self): return self.nombre

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email: raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Ensure a role exists for superuser
        rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
        extra_fields.setdefault('oid_rol', rol_admin)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    oid_usuario = models.AutoField(primary_key=True)
    oid_rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column='oid_rol', related_name='usuarios', null=True)
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
        db_table = 'usuario'
    def __str__(self): return f"{self.nombre} ({self.email})"

class TipoCaso(models.Model):
    oid_tipo_caso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, default='')
    class Meta: db_table = 'tipo_caso'
    def __str__(self): return self.nombre

class EstadoCaso(models.Model):
    oid_estado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    class Meta: db_table = 'estado_caso'
    def __str__(self): return self.nombre

class Caso(models.Model):
    oid_caso = models.AutoField(primary_key=True)
    oid_abogado = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='oid_abogado', related_name='casos')
    oid_tipo_caso = models.ForeignKey(TipoCaso, on_delete=models.PROTECT, db_column='oid_tipo_caso', related_name='casos')
    oid_estado = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT, db_column='oid_estado', related_name='casos')
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')
    numero_expediente = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField(null=True, blank=True)
    juzgado = models.CharField(max_length=100, blank=True, default='')
    class Meta:
        db_table = 'caso'
        ordering = ['-fecha_inicio']
    def __str__(self): return f"{self.numero_expediente} — {self.titulo}"

class CodigoLegal(models.Model):
    oid_codigo = models.AutoField(primary_key=True)
    nombre_norma = models.CharField(max_length=100)
    numero_articulo = models.CharField(max_length=50)
    texto_contenido = models.TextField()
    vigencia = models.BooleanField(default=True)
    class Meta:
        db_table = 'codigo_legal'
        ordering = ['nombre_norma', 'numero_articulo']
    def __str__(self): return f"{self.nombre_norma} — Art. {self.numero_articulo}"

class CasoNormativa(models.Model):
    oid_relacion = models.AutoField(primary_key=True)
    oid_caso = models.ForeignKey(Caso, on_delete=models.CASCADE, db_column='oid_caso')
    oid_codigo = models.ForeignKey(CodigoLegal, on_delete=models.CASCADE, db_column='oid_codigo')
    fecha_asociacion = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'caso_normativa'
        unique_together = ('oid_caso', 'oid_codigo')

class Documento(models.Model):
    oid_documento = models.AutoField(primary_key=True)
    oid_caso = models.ForeignKey(Caso, on_delete=models.CASCADE, db_column='oid_caso')
    nombre_archivo = models.CharField(max_length=150)
    ruta_archivo = models.FileField(upload_to='documentos/%Y/%m/')
    tipo_documento = models.CharField(max_length=50)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'documento'
        ordering = ['-fecha_subida']
