"""
ASGI config for farmetrics project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import WebSocket routing (will be created later)
# from apps.notifications.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket routing will be added here
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(
    #         URLRouter(
    #             websocket_urlpatterns
    #         )
    #     )
    # ),
})

