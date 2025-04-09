"""
ASGI config for liszteditor project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liszteditor.settings')

application = get_asgi_application()
