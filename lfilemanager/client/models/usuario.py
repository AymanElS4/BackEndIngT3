"""Modulo para el modelo Usuario — custom user model 
with email-based authentication."""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .rol import Rol


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
    """Modelo que representa a un usuario del sistema (abogados, admins, etc.)"""

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
    matricula_profesional = models.CharField(
        max_length=50, blank=True, default='')
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

    def save(self, *args, **kwargs):
        """Guarda el usuario y sincroniza el estado de activación de Django."""
        self.is_active = self.estado
        super().save(*args, **kwargs)

    def __str__(self):
        """Devuelve la representación en cadena del usuario."""
        return f"{self.nombre} ({self.email})"
