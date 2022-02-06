from django.apps import AppConfig

from blacksmith import scan

from ._settings import get_imports


class BlackmithConfig(AppConfig):
    name = "dj_blacksmith"
    verbose_name = "Blacksmith client"

    def ready(self):
        scan(*get_imports())
