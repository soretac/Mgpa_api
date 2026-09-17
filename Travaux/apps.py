from django.apps import AppConfig


class TravauxConfig(AppConfig):
    name = 'Travaux'

    def ready(self):
        import Travaux.SignalTravaux
