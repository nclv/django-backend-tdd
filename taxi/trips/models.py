from django.contrib.auth.models import AbstractUser


# Using this custom User model allows us to add fields to it later.
class User(AbstractUser):
    pass
