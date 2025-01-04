import factory
from .models import Room
from django.contrib.auth import get_user_model
from factory.mongoengine import MongoEngineFactory


User = get_user_model()


class User1Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = "user1@gmail.com"
    first_name = "John"
    last_name = "Doe"
    password = factory.PostGenerationMethodCall("set_password", "password1")


class User2Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = "user2@gmail.com"
    first_name = "Jane"
    last_name = "Doe"
    password = factory.PostGenerationMethodCall("set_password", "password2")


