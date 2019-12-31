from django.urls import path  # new
from channels.auth import AuthMiddlewareStack  # new
from channels.routing import ProtocolTypeRouter, URLRouter  # changed

from trips.consumers import TaxiConsumer

# If an http argument is not provided, it will default to the Django view system’s ASGI interface, channels.http.AsgiHandler, which means that for most projects that aren’t doing custom long-poll HTTP handling, you can simply not specify an http option and leave it to work the "normal" Django way.

application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter([path("taxi/", TaxiConsumer)]))}
)
