from django.apps import AppConfig


class MgpausersConfig(AppConfig):
    name = 'MgpaUsers'

    def ready(self):
        import MgpaUsers.SignalMgpaUsers
