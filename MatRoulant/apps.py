from django.apps import AppConfig


class MatroulantConfig(AppConfig):
    name = 'MatRoulant'

    def ready(self):
        import MatRoulant.SignalMatRoulant
