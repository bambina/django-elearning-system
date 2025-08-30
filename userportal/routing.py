from django.urls import path

from . import consumers

# Routing for websocket consumers
# Prefix the URL pattern with "ws" to indicate that this is a websocket URL
websocket_urlpatterns = [
    path(
        "ws/course/<int:course_id>/live-qa-session/<room_name>/",
        consumers.QASessionConsumer.as_asgi(),
    ),
]
