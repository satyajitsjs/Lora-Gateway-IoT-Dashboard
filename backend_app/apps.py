# backend_app/apps.py

from django.apps import AppConfig


class BackendAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend_app'

    # def ready(self):
    #     # Run custom management command on server startup
    #     from django.core import management
    #     management.call_command('startlora')