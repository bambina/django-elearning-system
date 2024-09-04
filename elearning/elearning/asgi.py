"""
ASGI config for elearning project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elearning.settings")

django_asgi_app = get_asgi_application()

# Load the routing configuration after the Django app is loaded
from userportal.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(  # Confirm that incoming WebSocket connections are from an allowed host
            # Add an authentication layer to WebSocket connections
            AuthMiddlewareStack(
                # Define the routing configuration for WebSocket connections
                URLRouter(websocket_urlpatterns)
            )
        ),
    }
)
