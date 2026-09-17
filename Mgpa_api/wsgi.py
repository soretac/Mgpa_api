"""
WSGI config for Mgpa_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

settings_module = 'Mgpa_api.deployment_settings' if 'RENDER_EXTERNAL_HOSTNAME' in os.environ else 'Mgpa_api.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mgpa_api.settings')

application = get_wsgi_application()
