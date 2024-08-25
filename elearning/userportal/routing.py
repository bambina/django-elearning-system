from django.urls import re_path

from . import consumers

# Routing for websocket consumers
# Prefix the URL pattern with "ws" to indicate that this is a websocket URL
websocket_urlpatterns = [
    re_path(
        r"ws/live-qa-session/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()
    ),
]
