import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from profiles.models import User, StartupProfile, InvestorProfile
from projects.models import Project


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password')


class StartupProfileFactory(DjangoModelFactory):
    class Meta:
        model = StartupProfile

    user = factory.SubFactory(UserFactory)


class InvestorProfileFactory(DjangoModelFactory):
    class Meta:
        model = InvestorProfile

    user = factory.SubFactory(UserFactory)
    email = factory.Faker('email')


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    startup = factory.SubFactory(StartupProfileFactory)
    funding_goal = Decimal("100.00")
    is_completed = False

