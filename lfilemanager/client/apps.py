"""Django AppConfig for the client application."""
from django.apps import AppConfig


class ClientConfig(AppConfig):
    """Configuration class for the client Django app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client'
