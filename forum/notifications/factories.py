import factory
import logging
from factory.django import DjangoModelFactory
from .models import NotificationType, StartUpNotification
from profiles.models import InvestorProfile, StartupProfile
from users.models import CustomUser, Role

factory.Faker._DEFAULT_LOCALE = 'en_US'
logging.getLogger('faker').setLevel(logging.INFO)

class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    role = Role.BOTH
    user_phone = factory.Faker('phone_number')
    title = 'some_title'
    is_staff = False
    is_active = True
    is_superuser = False


class InvestorProfileFactory(DjangoModelFactory):
    class Meta:
        model = InvestorProfile

    user = factory.SubFactory(UserFactory)
    country = factory.Faker('country')
    city = factory.Faker('city')
    zip_code = factory.Faker('postcode')
    address = factory.Faker('street_address')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')

class StartupProfileFactory(DjangoModelFactory):
    class Meta:
        model = StartupProfile

    user = factory.SubFactory(UserFactory)
    company_name = factory.Faker('company')
    industry = factory.Faker('word')
    size = factory.Faker('random_element', elements=('Small', 'Medium', 'Large'))
    country = factory.Faker('country')
    city = factory.Faker('city')
    zip_code = factory.Faker('postcode')
    address = factory.Faker('street_address')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')

class NotificationTypeFactory(DjangoModelFactory):
    class Meta:
        model = NotificationType

    name = factory.Faker('word')
    description = factory.Faker('text')

class StartUpNotificationFactory(DjangoModelFactory):
    class Meta:
        model = StartUpNotification

    notification_type = factory.SubFactory(NotificationTypeFactory)
    investor = factory.SubFactory(InvestorProfileFactory)
    startup = factory.SubFactory(StartupProfileFactory)
    is_read = False