# BackEndIng

## Requisitos

- Python 3.11 o superior
- pip
- virtualenv (recomendado)

## Instalación

1. Abrir una terminal en la carpeta del backend:

```bash
cd "c:\Users\Ayman El Salous Mnz\OneDrive\Desktop\proyectos\BackEndIng\BackEndIng\lfilemanager"
```

2. Crear e ingresar a un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Para iniciar el backend en modo desarrollo:

```bash
python manage.py runserver 0.0.0.0:8000
```

Esto levantará el backend en:

- http://127.0.0.1:8000/

## Comandos útiles

- Ejecutar comprobaciones de Django:

```bash
python manage.py check
```

- Crear migraciones:

```bash
python manage.py makemigrations
```

- Aplicar migraciones:

```bash
python manage.py migrate
```

- Ejecutar tests de Django:

```bash
python manage.py test
```
