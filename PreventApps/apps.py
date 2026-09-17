from django.apps import AppConfig


class PreventappsConfig(AppConfig):
    name = 'PreventApps'

    def ready(self):
        import PreventApps.SignalPrevent
