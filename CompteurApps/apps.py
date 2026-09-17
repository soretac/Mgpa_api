from django.apps import AppConfig


class CompteurappsConfig(AppConfig):
    name = 'CompteurApps'

    def ready(self):
        import CompteurApps.SignalComptApps
