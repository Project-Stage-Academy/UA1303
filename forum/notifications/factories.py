import factory
from factory.django import DjangoModelFactory
from .models import NotificationCategory, StartUpNotification, InvestorNotification
from profiles.models import InvestorProfile, StartupProfile
from users.models import CustomUser, Role
from projects.models import Project, Investment


class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Faker('email')
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

class InvestorNotificationFactory(DjangoModelFactory):
    class Meta:
        model = InvestorNotification

    notification_category = factory.SubFactory(NotificationCategoryFactory)
    investor = factory.SubFactory(InvestorProfileFactory)
    startup = factory.SubFactory(StartupProfileFactory)
    is_read = False

    def startup(self):
        return StartupProfileFactory()

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    startup = factory.SubFactory(StartupProfileFactory)
    title = factory.Faker('sentence', nb_words=4)
    funding_goal = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    is_published = True
    is_completed = False

    @factory.post_generation
    def set_completed(self, create, extracted, **kwargs):
        if extracted:
            self.is_completed = True
            self.save()

class InvestmentFactory(DjangoModelFactory):
    class Meta:
        model = Investment

    investor = factory.SubFactory(InvestorProfileFactory)
    project = factory.SubFactory(ProjectFactory)
    share = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)

    @factory.post_generation
    def ensure_project_published(self, create, extracted, **kwargs):
        if self.project and not self.project.is_published:
            self.project.is_published = True
            self.project.save()