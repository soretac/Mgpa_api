from django.apps import AppConfig


class EntrepriseConfig(AppConfig):
    name = 'Entreprise'

    def ready(self):
        import Entreprise.SignalEntreprise
