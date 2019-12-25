
## Introduction
https://testdriven.io/courses/real-time-app-with-django-channels-and-angular/

You'll learn how to program the server code of the ride-sharing application. We'll start by developing a custom user authentication model and profile data. Then we'll create a data model to track the trips that the riders and drivers participate in along with the APIs that provide access to that data. Lastly, we'll leverage the asynchronous nature of Django Channels to send and receive messages via WebSockets. Throughout this part, we'll be testing every function to make sure that the code we write operates the way we expect it to.

Tools and Technologies: (Asynchronous) Python, Django, Django REST Framework, Django Channels, Redis


## Uber App Using Django Channels
Many apps rely on real-time, bi-directional communication to give users a great experience. One example is a ride-sharing app like Uber or Lyft, which is built on the messages that are sent between a rider and a driver. A rider selects a starting location and destination, then broadcasts a trip request to all nearby drivers. An available driver accepts the trip and meets the rider at the pick-up address. In the meantime, every move the driver makes is sent to the rider almost instantaneously and the rider can track the trip status as long as it is active.

## Done

 * We added Django REST Framework along with our own trips app in ```INSTALLED_APPS``` in ```taxi/settings.py```
 * We also added an ```AUTH_USER_MODEL``` setting to make Django reference a user model of our design instead of the built-in one since we'll need to store more user data than what the standard fields allow.

    *Since we're creating this project from scratch, defining a custom user model is the right move. If we had made this change later in the project, we would have had to create a supplementary model and link it to the existing default user model.*

  * Create a basic custom user model in the ```trips/models.py``` file.
  * Make the first migration : ```python manage.py makemigrations```
  * Set up our app to use our custom user model : ```python manage.py migrate```. All database tables will be created as well.
  * Ensure all is well by running the server: ```python manage.py runserver```
  * Set up the Django admin page : ```python manage.py createsuperuser``` and modify ```trips/admin.py```.
  * Configure the ```CHANNEL_LAYERS``` by setting a default Redis backend and routing in the ```taxi/settings.py``` file.
  * Add Django Channels to the ```INSTALLED_APPS```.
  * Create a new file ```taxi/routing.py``` within our taxi app.
  * Find the ```WSGI_APPLICATION``` setting in ```taxi/settings.py``` and below that line add the following :
  ```python
  ASGI_APPLICATION = 'taxi.routing.application'
  ```
  Add then a new file ```taxi/asgi.py```.


## TODO
 * [ ] Create simple GET requests with Django REST Framework.
 * [ ] Implement token-based authentication.
 * [ ] Use Django Channels to create and update data on the server.
 * [ ] Send messages to the UI from the server via WebSockets.
 * [ ] Test asyncio coroutines with pytest.
