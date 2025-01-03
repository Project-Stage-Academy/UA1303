import os
import logging

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from communications.routing import websocket_urlpatterns

logger = logging.getLogger("django")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)


class LoggingMiddleware:
    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            raise
