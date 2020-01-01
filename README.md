
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

## HTTP

After users log in, they should be taken to a dashboard that displays an overview of their user-related data. Even though we plan to use WebSockets for user-to-user communication, we still have a use for run-of-the-mill HTTP requests. Users should be able to query the server for information about their past, present, and future trips. Up-to-date information is vital to understanding where the user has travelled from or for planning where she is traveling next.

Our HTTP-related tests capture these scenarios.

### All Trips

First, let's add a feature to let users view all of the trips associated with their accounts. As an initial step, we will allow users to see all existing trips; later on in this tutorial, we will add better filtering.

 * Add a test case to the bottom of our existing tests in ```trips/tests/test_http.py```. Our test creates two trips and then makes a call to the trip list API, which should successfully return the trip data. The test should fail ```python manage.py test trips.tests```.
 * First, we need to create a model that represents the concept of a trip. Update the ```trips/models.py``` file. Since a trip is simply a transportation event between a starting location and a destination, we included a pick-up address and a drop-off address. At any given point in time, a trip can be in a specific state, so we added a status to identify whether a trip is requested, started, in progress, or completed. Lastly, we need to have a consistent way to identify and track trips that is also difficult for someone to guess. So, we use a UUID for our Trip model.
 Let's make a migration for our new model and run it to create the corresponding table.
 ```sh
 (env)$ python manage.py makemigrations
 (env)$ python manage.py migrate
 ```
 * Now that our database has a Trip table, let's set up the corresponding admin page. Open ```trips/admin.py``` and register a ```TripAdmin```. Visit the admin page and add a new Trip record.
 * Like the user data, we need a way to serialize the trip data to pass it between the client and the server, so add a new serializer to the bottom of the ```trips/serializers.py``` file. By identifying certain fields as "read only", we can ensure that they will never be created or updated via the serializer. In this case, we want the server to be responsible for creating the ```id```, ```created```, and ```updated``` fields.
 * Add the ```TripView``` to ```trips/views.py```. As you can see, our ```TripView``` is incredibly basic. We leveraged the DRF ```ReadOnlyModelViewSet``` to support our trip list and trip detail views. For now, our view will return all trips. Note that like the ```LogOutView```, a user needs to be authenticated in order to access this API.
 * Include the trip-specific URL configuration in the main URLs file, ```taxi/urls.py```. Then, add our first trip-specific URL, which enables our ```TripView``` to provide a list of trips. Create a ```trips/urls.py``` file. 
 * Run again tests.
 
### Single Trip

Our next, and last, HTTP test covers the trip detail feature. With this feature, users are able to retrieve the details of a trip identified by its primary key (UUID) value.

 * Add the ```test_user_can_retrieve_trip_by_id``` to ```HttpTripTest``` in ```trips/tests/test_http.py```. Here, we leveraged the use of the handy ```get_absolute_url``` function on our ```Trip``` model to identify the location of our ```Trip``` resource. We added asserts that get the serialized data of a single trip and a success status.
 * Update the ```Tripview``` in ```trips/views.py```. Supporting our new functionality is as easy as adding two variables to our TripView:

    The ```lookup_field``` variable tells the view to get the trip record by its ```id``` value.
    The ```lookup_url_kwarg``` variable tells the view what named parameter to use to extract the ```id``` value from the URL.
    
 * Add the URL to ```trips/urls.py```. We identified a ```trip_id``` in our URL configuration, which should be a UUID.

## WebSockets

Up until now, we have dealt with users in a generic way: Users can authenticate and they can retrieve trips. The following section separates users into distinct roles, and this is where things get interesting. Fundamentally, users can participate in trips in one of two ways—they either drive the cars or they ride in them. A rider initiates the trip with a request, which is broadcasted to all available drivers. A driver starts a trip by accepting the request. At this point, the driver heads to the pick-up address. The rider is instantly alerted that a driver has started the trip and other drivers are notified that the trip is no longer up for grabs.

Instantaneous communication between the driver and the rider is vital here, and we can achieve it using WebSockets via Django Channels.

### Django Channels Setup

 * Create a new ```trips/tests/test_websocket.py``` file. There's a lot going on here. The first thing you'll notice is that we're using ```pytest``` instead of the built-in Django testing tools. We're also using coroutines that were introduced with the ```asyncio``` module in Python 3.4. Django Channels 2.x mandates the use of both ```pytest``` and ```asyncio```.
 Remember how we created HTTP test classes by extending ```APITestCase```? Grouping multiple tests with pytest only requires you to write a basic class. We named ours ```TestWebsockets```. We also decorated the class with two marks, which sets metadata on each of the test methods contained within. The ```@pytest.mark.asyncio``` mark tells pytest to treat tests as asyncio coroutines. The ```@pytest.mark.django_db``` mark allows tests to access the Django database. Specifying ```transaction=True``` ensures that the database will be flushed between tests.

 Let's look at the ```create_user()``` function next. Accessing the Django database is a synchronous operation as opposed to an asynchronous one, which means you need to handle it in a special way to ensure that the connections are closed properly. All functions that access the Django ORM should be decorated with ```@database_sync_to_async```.

 Finally, we come to the actual test. First, pay attention to the fact that we included a ```TEST_CHANNEL_LAYERS``` constant at the top of the file after the imports. We used that constant in the first line of our test along with the ```settings``` fixture provided by ```pytest-django```. This line of code effectively overwrites the application's settings to use the ```InMemoryChannelLayer``` instead of the configured ```RedisChannelLayer```. Doing this allows us to *focus our tests on the behavior we are programming rather than the implementation* with Redis. Rest assured that when we run our server in a non-testing  environment, Redis will be used.

 We went through a lot of trouble setting up authentication in earlier chapters of this course. Requests over ```WebSockets```  use authentication too. In the browser, every ```WebSockets``` request sends cookies (including our ```sessionid```) to the server. Remember, the ```sessionid``` cookie is saved in our browser after a successful login.
 
 We have to handle this behavior explicitly in our test by creating an instance of ```Client()``` and forcing a login with the authentication backend. Then we can extract the ```sessionid``` cookie from the ```Client``` and add it to our cookie header in our ```WebSockets``` request. We send this request using ```WebsocketCommunicator```, which is essentially the Channels counterpart to Django's ```Client```.
 
 * Add a ```pytest.ini``` file to the outermost directory. From the ```"server/taxi"``` directory, run the ```pytest``` tests and watch them fail.
 * We need to add a consumer, Channel's version of a Django view. Create a new ```trips/consumers.py``` file. We access the user from the ```scope``` like we would from a traditional Django ```request```. Funny how closely all of these features match up. Our ```connect()``` method accepts the connection if the user is authenticated and rejects it otherwise.
 * Now we need to update our ```routing.py``` file to get our tests to pass. This setup declares that all ```WebSockets``` requests should be passed through an ```AuthMiddlewareStack```, which processes cookies and handles session authentication. We also define routes with ```URLRouter``` in a way that is reminiscent of the Django urlconf.
 * Run the tests again.
 
We're going to have to create a user, authenticate it, and pass it in the request as part of every test from this point forward. Let's refactor our code to capture that behavior as part of each test's setup.
 * Add some code to the bottom of our ```trips/tests/test_websocket.py```. Then update the existing test to use it.

### Create Trips

 * Next, we're going to be handling the functionality that allows riders to create trips and drivers to update them. Add a new test to ```TestWebsockets``` in ```trips/tests/test_websocket.py```. After this test establishes an authenticated ```WebSockets``` connection, it sends a JSON-encoded message to the server, which will then create a new ```Trip``` and will return it to the client in a response. All messages should include a ```type```. Also, remember to disconnect from the server at the end of every test.
 * Add fields to the ```Trip``` model in ```trips/models.py```. We expanded our existing ```Trip``` model, in order to link a driver and a rider to a trip. Remember: Drivers and riders are just normal users that belong to different user groups. Later on, we'll see how the same app can serve both types of users and give each a unique experience.
 * Make and run migrations to update our ```Trip``` model database table : ```python manage.py makemigrations trips --name trip_driver_rider``` then ```python manage.py migrate```.
 * Let's update our admin page to reflect the changes we made in our model.
 
By default, our ```TripSerializer``` processes related models as primary keys. That is the exact behavior that we want when we use a serializer to create a database record. On the other hand, when we get the serialized ```Trip``` data back from the server, we want more information about the rider and the driver than just their database IDs.
 * Create a new ```ReadOnlyTripSerializer``` after our existing ```TripSerializer```. The difference is that the ```ReadOnlyTripSerializer``` serializes the full ```User``` object instead of its primary key.
 * Update the ```trips/consumers.py``` file. All incoming messages are received by the ```receive_json()``` method in the consumer. Here is where you should delegate the business logic to process different message types. Our ```create_trip()``` method creates a new trip and passes the details back to the client. Note that we are using a special decorated ```_create_trip()``` helper method to do the actual database update.
 * Let's do another round of refactoring to avoid duplicating code. Add an helper to the bottom of the ```trips/tests/test_websocket.py``` file. Update the test we just created too.
When a rider creates a trip, he should be automatically registered to receive updates about that trip, so that whenever a driver updates the trip, the rider will receive a notification.
 * Add a new test to ```trips/tests/test_websocket.py```. This test should prove that once a rider has created a trip, he gets added to a group to receive updates about it. Our test accesses that group and then sends a message to it via the ```group_send()``` method.
 * Update ```consumers.py```. Remember how we insisted on including a ```type``` in every message? Channels handles messages sent to groups (over channel layers) differently than it handles messages sent to the server directly by the client. Channels replaces all ```.``` in the message type with ```_``` and searches the consumer for a method name that matches. In this case, ```echo.message``` will access the ```echo_message()``` method.

Some other things to note:

    We initialize a ```trips``` list and keep track of the rider's trips during the life of the request. (We could also do this on the user's session if we wanted to.)
    When we create a trip, we add it to our tracked list. We also add the user to a group identified by the new trip's natural key value.
    We explicitly remove the user from each group when he disconnects. The ```asyncio.gather()``` method executes a list of asynchronous commands.

### Accessing Persistent Trip Data

We're successfully tracking a rider's trips as long as his session is alive. But what happens when that rider closes the app and then opens it again? We need to re-establish the connections to his groups.
 * Let's create a new test. Start by creating a new function to create a trip in the database.
 * Update the consumer again. We expanded the ```connect()``` method to retrieve the rider's trips and add the rider to each one's associated group. The ```_get_trips()``` method queries the database and needs to be decorated appropriately. We don't want to add the rider to the same trip twice.

### Update trips

 * Let's handle the functionality to update existing trips. Start with a test. We can already anticipate needing to reuse updating behavior, so we can avoid refactoring by adding a proper service function now. In this test, we are explicitly updating an existing trip's status from ```REQUESTED``` to ```IN_PROGRESS```. We send the request, the server updates the trip, we confirm that the response data matches our expectations.
 * Edit the consumer to handle updates. We have a new event type—update.trip. We created corresponding ```update_trip()``` and ```_update_trip()``` methods to process the event. Updating the trip adds the driver to the associated trip group.
 * Add one more test for the driver. The driver should receive a notification of any updates that occur on the trip. This test does not require any changes to the consumer.
 * All drivers should be alerted whenever a new trip is created. Riders should be alerted when a driver updates the trip that they created. Add tests to capture that behavior.
 * We need to update some of our consumer's methods to accommodate the driver. First, we check whether the user is a driver when the ```WebSocket``` connection is established. If he is, then we subscribe him to the drivers group. Next, we alert all drivers when a rider broadcasts a trip request.

 When a driver accepts a request, we need to alert the corresponding rider every time the driver updates the trip's status. For example, the rider should get a message like "your ride is on its way". Lastly, a driver should be removed from the drivers group when he closes his WebSocket connection by exiting the app.

## UI support

Up until now, we haven't had a reason to track users as drivers or riders. Users can be either. But as soon as we add a UI, we will need a way for users to sign up with a role. Drivers will see a different UI and will experience different functionality than riders.

 * The first thing we need to do is add support for user groups in our serializers in ```trips/serializers.py```.
 * Next, update the custom user model in ```trips/models.py``` to support groups as well. We are not adding any database fields so we don't need to create a new migration.
 * Lastly, add the proper filters to the ```TripView``` in ```trips/views.py```.
 * First, within ```trips/tests/test_http.py```, update the ```create_user()``` function to take an additional ```group_name``` parameter. And add the ```group``` to the ```test_user_can_sign_up``` test in ```AuthenticationTest```. Next, update ```HttpTripTest```.
After modifications, all tests should pass. ```python manage.py test trips.tests```

 * Finally, run the server and test out the DRF Browsable API:
    http://localhost:8000/api/sign_up/
    http://localhost:8000/api/log_in/s

## User Photos

Viewing a user's photo is an important piece of functionality in ride-sharing apps. In fact, most of these apps make it mandatory to provide a photo before you can drive or ride. From one perspective, it's a security issue—riders need to confirm that the drivers are who they expect before they enter their vehicles. User photos are also good design and add life to the product.

Our app will allow users to add their photos at sign up.

### Media Files

Media files are a form of user-generated static files and Django handles both in a similar way. We need to provide two new settings, ```MEDIA_ROOT``` and ```MEDIA_URL```.

The ```MEDIA_ROOT``` is the path to the directory where file uploads will be saved. For the purpose of this tutorial, we can create a "media" folder inside our "server" directory. In a production environment, we'd specify an absolute path to a directory on the server or we'd store files with a service like AWS S3. The ```MEDIA_URL``` is the prefix to use in our URL path.

 * Set both the ```MEDIA_URL``` and the ```MEDIA_ROOT``` within the settings file.
 * One last step is required to get our local environment to serve media files. Update ```taxi/urls.py```.

 Media files can now be retrieved via ```http://localhost:8000/media/<file_path>/``` on your local machine.
 
 To test, add a new folder called media to server. Then, add a test file called *test.txt* to that folder and add some random text to the file. Fire up the server and navigate to ```http://localhost:8000/media/test.txt``` to view the file.

     *Make sure you remove the ```static()``` function from the urlpatterns when you deploy your application. We only need that for local development.*

 * Change the existing ```AuthenticationTest.test_user_can_sign_up``` test. Add the ```create_photo_file``` helper function right after the ```create_user``` helper. This code leverages the ```Pillow``` library, ```BytesIO``` from the standard library, and Django's ```SimpleUploadedFile``` to create fake image data. Of course the test will fail since we need to update our user model and its serializer.
 * Modify the user model. Now, when users upload their photos, the app will save them in a photos subdirectory within our media folder.

In order to display a photo, we need either the relative URL (i.e. ```/media/photos/photo.jpg```) or the absolute URL (i.e. ```http://localhost:8080/media/photos/photo.jpg```). Django REST Framework provides a ```use_url=True``` property on its ```ImageField``` class, but the absolute URL it provides does not include the port. We can get around this shortcoming by creating our own custom serializer field.

 * Edit the ```serializers.py``` file to create and use a new ```MediaImageField```.
 * Edit the ```views.py``` file to make ```TripView``` use the ```ReadOnlyTripSerializer```. We want the Trip API response payload to include full driver and rider object representations.
 * One last thing—create a migration for the new ```photo``` field on our user table and run the migrations.
 * Now the tests should pass. ```python manage.py test trips.tests```


## TODO
 * [x] Create simple GET requests with Django REST Framework.
 * [x] Implement token-based authentication.
 * [x] Use Django Channels to create and update data on the server.
 * [x] Send messages to the UI from the server via WebSockets.
 * [x] Test asyncio coroutines with pytest.
