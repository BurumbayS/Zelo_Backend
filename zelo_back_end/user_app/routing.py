from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .middleware import JWTAuthMiddleware

from . import consumers

websocket_urlpatterns = [
    path('ws/', consumers.ChatConsumer),
]

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': JWTAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
        ),
})
