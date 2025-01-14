import factory
from factory.django import DjangoModelFactory
from .models import NotificationCategory, StartUpNotification
from profiles.models import InvestorProfile, StartupProfile
from users.models import CustomUser, Role


class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    role = Role.BOTH
    user_phone = factory.Faker('phone_number')
    title = "some_title"
    is_staff = False
    is_active = True
    is_superuser = False


class InvestorProfileFactory(DjangoModelFactory):
    class Meta:
        model = InvestorProfile

    user = factory.SubFactory(UserFactory)
    country = factory.Faker('country_code', representation='alpha-2')
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
    country = factory.Faker('country_code', representation='alpha-2')
    city = factory.Faker('city')
    zip_code = factory.Faker('postcode')
    address = factory.Faker('street_address')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')

class NotificationCategoryFactory(DjangoModelFactory):
    class Meta:
        model = NotificationCategory

    name = factory.Faker('word')
    description = factory.Faker('text')

class StartUpNotificationFactory(DjangoModelFactory):
    class Meta:
        model = StartUpNotification

    notification_category = factory.SubFactory(NotificationCategoryFactory)
    investor = factory.SubFactory(InvestorProfileFactory)
    startup = factory.SubFactory(StartupProfileFactory)
    is_read = False