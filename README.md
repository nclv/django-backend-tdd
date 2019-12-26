
## Introduction
https://testdriven.io/courses/real-time-app-with-django-channels-and-angular/

You'll learn how to program the server code of the ride-sharing application. We'll start by developing a custom user authentication model and profile data. Then we'll create a data model to track the trips that the riders and drivers participate in along with the APIs that provide access to that data. Lastly, we'll leverage the asynchronous nature of Django Channels to send and receive messages via WebSockets. Throughout this part, we'll be testing every function to make sure that the code we write operates the way we expect it to.

Tools and Technologies: (Asynchronous) Python, Django, Django REST Framework, Django Channels, Redis


## Uber App Using Django Channels
Many apps rely on real-time, bi-directional communication to give users a great experience. One example is a ride-sharing app like Uber or Lyft, which is built on the messages that are sent between a rider and a driver. A rider selects a starting location and destination, then broadcasts a trip request to all nearby drivers. An available driver accepts the trip and meets the rider at the pick-up address. In the meantime, every move the driver makes is sent to the rider almost instantaneously and the rider can track the trip status as long as it is active.

## Getting started

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
  * Add then a new file ```taxi/asgi.py```.

## Authentication

Authentication is the cornerstone of any app that handles user data. It allows users to maintain privacy within the app, while gaining access to the full set of features afforded with registration.

With Django REST Framework (DRF), we have four authentication classes to choose from:

    BasicAuthentication
    TokenAuthentication
    SessionAuthentication
    RemoteUserAuthentication

We can eliminate ```BasicAuthentication``` right off the bat because it doesn't offer enough security for production environments. Although it is an attractive option because it supports both desktop and mobile clients, we can rule out ```TokenAuthentication``` too. The ```TokenAuthentication``` backend works by issuing an authentication token to the user after login. The client must send that token as a header to authorize subsequent requests. Unfortunately, the WebSockets browser APIs do not allow custom headers and neither does Django Channels. Between the remaining two classes, we should use ```SessionAuthentication``` because both HTTP and WebSockets requests can use it without any problems. Using the ```SessionAuthentication``` backend has the added benefit of offering arbitrary user data storage during the life of the session.

### Sign Up

 * Add ```REST_FRAMEWORK``` to ```taxi/settings.py```.

 Let's create a new user account via an API. Users should be able to download our app and immediately sign up for a new account by providing the bare minimum of information—username, password, and their names. The distinction between ```password1``` and ```password2``` correlates to users entering their passwords and then confirming them. Eventually, our app will present users a form with input fields and a submit button.

 * Remove the existing ```trips/tests.py``` file and create a new ```"tests/"``` directory inside of ```"trips/"```. Within it add an empty ```__init__.py``` file along with a ```test_http.py``` file.
 *We expect our API to return a 201 status code when the user account is created.
 The response data should be a JSON-serialized representation of our user model.*
 ```python manage.py test trips.tests``` to run the tests. It will fail.

Typically, a data model is the first thing we want to create in a situation like this. We've already created a user model, and since it extends Django's built-in model, it already supports the fields we need. The next bit of code we need is the user serializer.
 * Create a new ```trips/serializers.py``` file.
 *We should never need to read the password*
 * Open the ```trips/views.py``` file and add the ```SignUpView``` view.

Here, we created a ```SignUpView``` that extends Django REST Framework's ```CreateAPIView``` and leverages our ```UserSerializer``` to create a new user.

Here's how it works behind the scenes:

   Django passes request data to the ```SignUpView```, which in turn attempts to create a new user with the ```UserSerializer```. The serializer checks if the passwords match.
   If all of the data is valid, the serializer creates and returns a new user. If it fails, then the serializer returns the errors. Even if the passwords match, validation could fail if the username is already taken or the password isn't strong enough.

 * Configure a URL to link to our view by updating the existing ```taxi/urls.py``` file.

Now tests should pass.
To manually test, fire up the server ```python manage.py runserver``` and navigate to the Browsable API at ```http://localhost:8000/api/sign_up/```.
Take note of the following error:
```
HTTP 405 Method Not Allowed
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "detail": "Method \"GET\" not allowed."
}
```
That's expected since we don't have a GET route set up. You can still test out the POST functionality using the HTML form.

### Log in and out

 * Add two new tests to handle the log in and log out behavior to ```trips/tests/test_http.py```.

The process of logging in is as easy as signing up: The user enters her username and password and submits them to the server. We expect the server to log the user in and then return a success status along with the serialized user data.

Logging out is even simpler—the action returns a successful status code with no content.

 * Update ```trips/views.py```.

We programmed our log in and log out functions as we planned in the tests. Let's break each view down:

   In our ```LogInView```, we leveraged Django's ```AuthenticationForm```, which expects a username and password to be provided. We validated the form to get an existing user and then we logged that user in.
   Our ```LogOutView``` does the opposite of the ```LogInView```: It logs the user out. We added an ```IsAuthenticated``` permission to ensure that only logged-in users can log out.

 * Link our new views to URLs in the existing configuration in ```taxi/urls.py```

### Sanity checks

You can also test via cURL in a new Terminal console. Make sure the server is still running!

First sign up for a new account:
```bash
$ curl -X POST http://localhost:8000/api/sign_up/ \
-H 'Content-Type: application/json' \
-d '
{
    "username": "michael@something.com",
    "password1": "test",
    "password2": "test",
    "first_name": "michael",
    "last_name": "herman"
}
'
```
```bash
{
  "id": 5,
  "username": "michael@something.com",
  "first_name": "michael",
  "last_name": "herman"
}
```

And then attempt to log in with the same credentials:
```bash
$ curl -X POST http://localhost:8000/api/log_in/ \
-H 'Content-Type: application/json' \
-d '
{
    "username": "michael@something.com",
    "password": "test"
}
'
```
```bash
{
  "id": 5,
  "username": "michael@something.com",
  "first_name": "michael",
  "last_name": "herman"
}
```


## TODO
 * [ ] Create simple GET requests with Django REST Framework.
 * [ ] Implement token-based authentication.
 * [ ] Use Django Channels to create and update data on the server.
 * [ ] Send messages to the UI from the server via WebSockets.
 * [ ] Test asyncio coroutines with pytest.
