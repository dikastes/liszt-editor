"""
WSGI config for liszteditor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liszteditor.settings')

application = get_wsgi_application()
