import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lfilemanager.settings')
django.setup()

from client.models import Rol, TipoCaso, EstadoCaso, Usuario

def seed():
    print("Seeding database...")
    
    # Roles
    roles = [
        ('Básico', 'Usuario con acceso básico'),
        ('Profesional', 'Abogado con acceso profesional'),
        ('Empresa', 'Firma con acceso multi-usuario'),
        ('Administrador', 'Administrador total del sistema')
    ]
    for nombre, desc in roles:
        Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
    print("- Roles created.")

    # Tipos de Caso
    tipos = [
        ('Civil', 'Derecho civil y contratos'),
        ('Penal', 'Derecho penal y delitos'),
        ('Laboral', 'Derecho del trabajo'),
        ('Corporativo', 'Derecho de empresas'),
        ('Constitucional', 'Amparos y derechos humanos')
    ]
    for nombre, desc in tipos:
        TipoCaso.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
    print("- Tipos de caso created.")

    # Estados de Caso
    estados = ['Pendiente', 'Activo', 'Cerrado', 'Histórico', 'Archivado']
    for nombre in estados:
        EstadoCaso.objects.get_or_create(nombre=nombre)
    print("- Estados de caso created.")

    # Admin User
    if not Usuario.objects.filter(email='admin@legalfile.com').exists():
        Usuario.objects.create_superuser(
            email='admin@legalfile.com',
            password='admin123',
            nombre='Admin Sistema'
        )
        print("- Admin user created (admin@legalfile.com / admin123).")

if __name__ == '__main__':
    seed()
