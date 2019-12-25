
# Introduction
https://testdriven.io/courses/real-time-app-with-django-channels-and-angular/

You'll learn how to program the server code of the ride-sharing application. We'll start by developing a custom user authentication model and profile data. Then we'll create a data model to track the trips that the riders and drivers participate in along with the APIs that provide access to that data. Lastly, we'll leverage the asynchronous nature of Django Channels to send and receive messages via WebSockets. Throughout this part, we'll be testing every function to make sure that the code we write operates the way we expect it to.

Tools and Technologies: (Asynchronous) Python, Django, Django REST Framework, Django Channels, Redis


# Uber App Using Django Channels
Many apps rely on real-time, bi-directional communication to give users a great experience. One example is a ride-sharing app like Uber or Lyft, which is built on the messages that are sent between a rider and a driver. A rider selects a starting location and destination, then broadcasts a trip request to all nearby drivers. An available driver accepts the trip and meets the rider at the pick-up address. In the meantime, every move the driver makes is sent to the rider almost instantaneously and the rider can track the trip status as long as it is active.

