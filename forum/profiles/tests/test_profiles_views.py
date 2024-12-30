from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from profiles.models import InvestorProfile, StartupProfile
from profiles.serializers import InvestorProfileSerializer

User = get_user_model()


class InvestorProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="securepassword"
        )

    def test_profile_creation(self):
        profile = InvestorProfile.objects.create(
            user=self.user,
            country="Ukraine",
            phone="A test startup",
            email="testcase@gmail.com",
        )

        self.assertEqual(profile.country, "Ukraine")
        self.assertEqual(profile.user, self.user)

    def test_profile_creation_invalid_email(self):
        data = {
            "user": self.user.user_id,
            "country": "Ukraine",
            "phone": "+380991234567",
            "email": "invalid-email",
        }

        serializer = InvestorProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(serializer.errors["email"][0], "Enter a valid email address.")

    def test_profile_creation_empty_email(self):
        data = {
            "user": self.user.user_id,
            "country": "Ukraine",
            "phone": "+380991234567",
        }

        serializer = InvestorProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["email"][0], "This field is required.")

    def tearDown(self):
        del self.user


class InvestorProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="securepassword"
        )
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.data = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@example.com",
            "account_balance": 1500.75,
        }

        self.invalid_data = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@ex@mple.com",
            "account_balance": 1500.75,
        }

        self.missing_email_data = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "account_balance": 1500.75,
        }

        self.missing_phone_data = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@example.com",
            "account_balance": 1500.75,
        }

        self.invalid_balance_data_smaller_balance = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "email": "investor@example.com",
            "account_balance": -60.65,
        }

        self.invalid_phone_data = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "invalid_phone",
            "email": "investor@example.com",
            "account_balance": 1500.75,
        }

        self.invalid_balance_data_bigger_balance = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@example.com",
            "account_balance": 999999999 * 999999999,
        }
        self.valid_balance_data_big_balance = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@example.com",
            "account_balance": 9999999999999.99,
        }

        self.invalid_zipcode = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "zip-code",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@example.com",
            "account_balance": 1500.75,
        }

    def create_profile(self, data):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, data, format="json")
        return response

    def test_create_investor_profile(self):
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["country"], self.data["country"])
        self.assertEqual(response.data["email"], self.data["email"])

    def test_invalid_create_investor_profile(self):
        response = self.create_profile(self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_investor_profile_missing_email(self):
        response = self.create_profile(self.missing_email_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_create_investor_profile_invalid_phone(self):
        response = self.create_profile(self.invalid_phone_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

    def test_create_investor_profile_missing_phone(self):
        response = self.create_profile(self.missing_phone_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("phone", response.data)

    def test_create_profile_invalid_zipcode_type(self):
        response = self.create_profile(self.invalid_zipcode)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("zip_code", response.data)

    def test_create_investor_profile_invalid_balance_bigger(self):
        response = self.create_profile(self.invalid_balance_data_bigger_balance)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account_balance", response.data)

    def test_create_investor_profile_valid_balance_big(self):
        response = self.create_profile(self.valid_balance_data_big_balance)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("account_balance", response.data)

    def test_create_investor_profile_invalid_balance_smaller(self):
        response = self.create_profile(self.invalid_balance_data_smaller_balance)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account_balance", response.data)

    def test_update_investor_profile(self):
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        investor_profile_id = response.data["id"]

        update_url = reverse(
            "profiles:investor-profile-detail", args=[investor_profile_id]
        )
        updated_data = self.data.copy()
        updated_data["city"] = "Kyiv"
        response = self.client.put(update_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], updated_data["city"])
        self.assertEqual(response.data["address"], updated_data["address"])

    def test_partial_update_investor_profile(self):
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        investor_profile_id = response.data["id"]

        partial_update_url = reverse(
            "profiles:investor-profile-detail", args=[investor_profile_id]
        )
        partial_update_data = {"city": "Odessa"}
        response = self.client.patch(
            partial_update_url, partial_update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], partial_update_data["city"])
        self.assertEqual(response.data["country"], self.data["country"])

    def test_delete_investor_profile(self):
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        investor_profile_id = response.data["id"]

        delete_url = reverse(
            "profiles:investor-profile-detail", args=[investor_profile_id]
        )
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_access_to_create_profile(self):
        self.client.credentials()
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_detail_view(self):
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["city"], self.data["city"])
        self.assertEqual(response.data["country"], self.data["country"])
        profile_id = response.data["id"]

        self.client.credentials()

        detail_url = reverse("profiles:investor-profile-detail", args=[profile_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_delete_profile(self):
        response = self.create_profile(self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["city"], self.data["city"])
        self.assertEqual(response.data["country"], self.data["country"])
        profile_id = response.data["id"]

        self.client.credentials()

        delete_url = reverse("profiles:investor-profile-detail", args=[profile_id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        del self.user
        del self.token
        InvestorProfile.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()


class InvestorProfileOwnershipTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com", password="securepassword"
        )
        self.owner_token = AccessToken.for_user(self.owner)

        self.other_user = User.objects.create_user(
            email="otheruser@example.com", password="securepassword"
        )
        self.other_user_token = AccessToken.for_user(self.other_user)

        self.data = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
            "email": "investor@example.com",
            "account_balance": 1500.75,
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.owner_token}")
        response = self.client.post(
            reverse("profiles:investor-profile-list"), self.data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.profile_id = response.data["id"]

    def test_other_user_cannot_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other_user_token}")
        update_url = reverse("profiles:investor-profile-detail", args=[self.profile_id])
        updated_data = {"city": "Kyiv"}
        response = self.client.put(update_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other_user_token}")
        delete_url = reverse("profiles:investor-profile-detail", args=[self.profile_id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        del self.owner
        del self.other_user
        del self.other_user_token
        del self.owner_token
        InvestorProfile.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()


class StartupProfileTestCase(APITestCase):
    def setUp(self):
        # Creating users. User1 is startup owner.
        self.user1 = User.objects.create_user(password='password1', email='user1@email.com')
        self.user2 = User.objects.create_user(password='password2', email='user2@email.com')

        # Create tokens for authorization
        self.token_user1 = self.get_jwt_token(self.user1)
        self.token_user2 = self.get_jwt_token(self.user2)

        # Create profile for user1
        self.startup1 = StartupProfile.objects.create(
            user=self.user1,
            company_name='SuperCompany',
            industry='transport',
            size='100',
            country='USA',
            city='Los Angeles',
            zip_code='2000',
            address='Some street 7',
            phone='+380632225577',
            email='random@email.com',
            description='Some description',
        )

    def get_jwt_token(self, user):
        """Helper method to create a JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_anonymous_get_startup_request(self):
        """Test that user can't access the protected endpoint without login."""
        url = reverse('profiles:profiles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_update_startup_profile(self):
        """Test that anonymous user cannot update startup profile."""
        url = reverse('profiles:profiles-detail', kwargs={'pk': self.startup1.pk})
        data = {
            "company_name": "Renamed company",
            "industry": "transport",
            "size": "100",
            "country": "USA",
            "city": "Los Angeles",
            "zip_code": "2000",
            "address": "Some street 6",
            "phone": "+380632225577",
            "email": "random@email.com",
            "description": "Amazing company that should not be created"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_startup_request(self):
        """Test that authenticated user can access the protected endpoint"""
        url = reverse('profiles:profiles-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_startup_profile(self):
        """Test that user 2 can create profile"""
        url = reverse('profiles:profiles-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        data = {
            "company_name": "New company",
            "industry": "finance",
            "size": "200",
            "country": "USA",
            "city": "Washington",
            "zip_code": "2000",
            "address": "new street 16",
            "phone": "+380632225577",
            "email": "use22222r@example.com",
            "description": "Amazing company that should be created"
        }
        response = self.client.post(url, data, format='json')
        startup = StartupProfile.objects.get(user=self.user2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(startup.user, self.user2)
        self.assertEqual(startup.company_name, data["company_name"])
        self.assertEqual(startup.industry, data["industry"])
        self.assertEqual(startup.size, data["size"])
        self.assertEqual(startup.country, data["country"])
        self.assertEqual(startup.city, data["city"])
        self.assertEqual(startup.zip_code, data["zip_code"])
        self.assertEqual(startup.address, data["address"])
        self.assertEqual(startup.phone, data["phone"])
        self.assertEqual(startup.email, data["email"])
        self.assertEqual(startup.description, data["description"])

    def test_create_startup_profile_required_fields(self):
        """Test that user 2 can create profile without optional fields"""
        url = reverse('profiles:profiles-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        data = {
            "company_name": "New company",
            "industry": "finance",
            "size": "200",
            "country": "USA",
            "city": "Washington",
            "zip_code": "2000",
            "address": "",
            "phone": "",
            "email": "use22222r@example.com",
            "description": ""
        }
        response = self.client.post(url, data, format='json')
        startup = StartupProfile.objects.get(user=self.user2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(startup.user, self.user2)

    def test_email_validation(self):
        """Test email validation"""
        url = reverse('profiles:profiles-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        data = {
            "company_name": "New company",
            "industry": "finance",
            "size": "200",
            "country": "USA",
            "city": "Washington",
            "zip_code": "2000",
            "address": "new street 16",
            "phone": "+380632225577",
            "email": "use22222r@example",
            "description": "Amazing company that should be created"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_phone_validation(self):
        """Test phone validation"""
        url = reverse('profiles:profiles-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        data = {
            "company_name": "New company",
            "industry": "finance",
            "size": "200",
            "country": "USA",
            "city": "Washington",
            "zip_code": "2000",
            "address": "new street 16",
            "phone": "+3806322",
            "email": "use22222r@example.com",
            "description": "Amazing company that should be created"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_second_startup_profile(self):
        """Test that user1 can't create second profile"""
        url = reverse('profiles:profiles-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "company_name": "Second company",
            "industry": "finance",
            "size": "240",
            "country": "USA",
            "city": "Washington",
            "zip_code": "3000",
            "address": "new street 22",
            "phone": "+380632225477",
            "email": "use24422r@example.com",
            "description": "Amazing company that should not be created"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_partial_update_startup_profile(self):
        """Test for user to update existing profile"""
        url = reverse('profiles:profiles-detail', kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "company_name": "Renamed company",
            "industry": "transport",
            "size": "100",
            "country": "USA",
            "city": "Los Angeles",
            "zip_code": "2000",
            "address": "Some street 6",
            "phone": "+380632225577",
            "email": "random@email.com",
            "description": "Amazing company that should not be created"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.startup1.refresh_from_db()
        self.assertEqual(self.startup1.company_name, 'Renamed company')
        self.assertEqual(self.startup1.description, 'Amazing company that should not be created')

    def test_delete_startup_restricted(self):
        """Test for user to protect startup profiles from deletion if user is not a startup owner"""
        url = reverse('profiles:profiles-detail', kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_delete_startup_profile(self):
        """Test for user to protect startup profiles from deletion if user is not logged in"""
        url = reverse('profiles:profiles-detail', kwargs={'pk': self.startup1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_startup_profile(self):
        """Test for user to delete startup if user is a startup owner"""
        url = reverse('profiles:profiles-detail', kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProfile.objects.filter(pk=self.startup1.pk).exists())


class SaveProfileTestCase(APITestCase):

    save_startup_url = 'profiles:startups-save-favorite'
    unsave_startup_url = 'profiles:startups-delete-favorite'

    def setUp(self):
        # Creating users. User1 is startup owner. User 2 is investor
        self.user1 = User.objects.create_user(password='password1', email='user1@email.com')
        self.user2 = User.objects.create_user(password='password2', email='user2@email.com')

        # Create tokens for authorization
        self.token_user1 = self.get_jwt_token(self.user1)
        self.token_user2 = self.get_jwt_token(self.user2)

        # Create startup profile for user1
        self.startup1 = StartupProfile.objects.create(
            user=self.user1,
            company_name='SuperCompany',
            industry='transport',
            size='100',
            country='USA',
            city='Los Angeles',
            zip_code='2000',
            address='Some street 7',
            phone='+380632225577',
            email='random@email.com',
            description='Some description',
        )

        # Create Investor profile for user 2
        self.investor1 = InvestorProfile.objects.create(
            user=self.user2,
            country="Ukraine",
            phone="+380631234455",
            email="testcase@gmail.com",
        )

    def get_jwt_token(self, user):
        """Helper method to create a JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_anonymous_save_startup_request(self):
        """Test that user can't access the protected endpoint without login."""
        url = reverse(self.save_startup_url, kwargs={'pk': self.startup1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_save_startup(self):
        """Positive test to save startup to favourites"""
        url = reverse(self.save_startup_url, kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_save_startup_wrong_user(self):
        """Negative test to save startup to favourites when user has no investor profile"""
        url = reverse(self.save_startup_url, kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_startup_wrong_startup_id(self):
        """Negative test to save startup to favourites when startup does not exist"""
        invalid_startup_id = StartupProfile.objects.order_by(
            '-id').first().id + 1 if StartupProfile.objects.exists() else 1
        url = reverse(self.save_startup_url, kwargs={'pk': invalid_startup_id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_save_startup_second_time(self):
        """Negative test to save startup to favourites if startup is already followed"""
        url = reverse(self.save_startup_url, kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        self.client.post(url)
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_favorite_startup_anonymous(self):
        """Test that anonymous user has no access to the endpoint"""
        url = reverse(self.unsave_startup_url, kwargs={'pk': self.startup1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_favorite_startup(self):
        """Test removing startup from saved favorites"""

        # Saving startup first
        save_url = reverse(self.save_startup_url, kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        save_response = self.client.post(save_url)

        # Unsaving startup
        unsave_url = reverse(self.unsave_startup_url, kwargs={'pk': self.startup1.pk})
        response = self.client.delete(unsave_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.startup1.followers.filter(pk=self.user2.pk).exists())

    def test_delete_not_existing_favorite_startup(self):
        """Test removing startup that not exists from saved favorites"""
        url = reverse(self.unsave_startup_url, kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        del self.token_user1
        del self.token_user2
        InvestorProfile.objects.all().delete()
        StartupProfile.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()


class ListSavedProfilesTestCase(APITestCase):

    get_saved_startups_url = 'profiles:startups-list'

    def setUp(self):

        self.startup1_name = 'SuperCompany'
        self.startup1_industry = 'transport'
        self.startup1_size = '100'
        self.startup1_country = 'United Kingdom'
        self.startup1_city = 'Los Angeles'

        # Creating users and their startup profiles
        self.user1 = User.objects.create_user(password='password1', email='user1@email.com')
        self.startup1 = StartupProfile.objects.create(
            user=self.user1,
            company_name=self.startup1_name,
            industry=self.startup1_industry,
            size=self.startup1_size,
            country=self.startup1_country,
            city=self.startup1_city,
            zip_code='90002',
            address='Some street 7',
            phone='+380632225577',
            email='random@email.com',
            description='Some description',
        )
        self.user2 = User.objects.create_user(password='password2', email='user2@email.com')
        self.startup2 = StartupProfile.objects.create(
            user=self.user2,
            company_name='Small Business',
            industry='tourism',
            size='200',
            country='USA',
            city='London',
            zip_code='E1 6AN',
            address='Some street 74',
            phone='+380632225522',
            email='randdsaom@email.com',
            description='Some description',
        )

        # 3rd user will be acting as investor
        self.user3 = User.objects.create_user(password='password3', email='user3@email.com')
        self.investor = InvestorProfile.objects.create(
            user=self.user3,
            country="Ukraine",
            phone="+380631234455",
            email="testca3se@gmail.com",
        )

        # Adding startups to favourites
        startups = [self.startup1, self.startup2]
        self.investor.followed_startups.add(*startups)

        # Generating user's access token
        self.token_user3 = self.get_jwt_token(self.user3)

    def get_jwt_token(self, user):
        """Helper method to create a JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_get_followed_startups_anonymous(self):
        """Test that checks if anonymous user has no access to the protected endpoint"""
        url = reverse(self.get_saved_startups_url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_followed_startups(self):
        """Test that checks if authorized user can get list of startups"""
        url = reverse(self.get_saved_startups_url)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user3}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def search_and_assert(self, search_query, search_field: str, expected_count: int):
        """Helper method to perform search and assert results."""
        url = reverse(self.get_saved_startups_url) + f'?search={search_query}'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user3}')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_count)
        for item in response.data:
            self.assertIn(search_query, item[search_field])

    def filter_and_assert(self, filter_queries: dict, expected_count: int):
        """Helper method to perform filter and assert results."""
        query_params = '&'.join([f'{field}={value}' for field, value in filter_queries.items()])
        url = reverse(self.get_saved_startups_url) + '?' + query_params
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user3}')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_count)
        if expected_count > 0:
            for item in response.data:
                for field, search_query in filter_queries.items():
                    self.assertEqual(search_query, item.get(field))

    def test_get_followed_startups_name_search(self):
        """Test search by name"""
        search_query = self.startup1_name[0:-2]
        search_field = 'company_name'
        self.search_and_assert(search_query, search_field, 1)

    def test_get_followed_startups_industry_search(self):
        """Test search by industry"""
        search_query = self.startup1_industry[0:-2]
        search_field = 'industry'
        self.search_and_assert(search_query, search_field, 1)

    def test_get_followed_startups_country_search(self):
        """Test search by country"""
        search_query = self.startup1_country[0:-2]
        search_field = 'country'
        self.search_and_assert(search_query, search_field, 1)

    def test_get_followed_startups_city_search(self):
        """Test search by city"""
        search_query = self.startup1_city[0:-2]
        search_field = 'city'
        self.search_and_assert(search_query, search_field, 1)

    def test_get_followed_startups_industry_filter(self):
        """Test filter by industry"""
        search_query = {'industry': self.startup1_industry}
        self.filter_and_assert(search_query, 1)

    def test_get_followed_startups_country_filter(self):
        """Test filter by country"""
        search_query = {'country': self.startup1_country}
        self.filter_and_assert(search_query, 1)

    def test_get_followed_startups_city_filter(self):
        """Test filter by city"""
        search_query = {'city': self.startup1_city}
        self.filter_and_assert(search_query, 1)

    def test_get_followed_startups_size_filter(self):
        """Test filter by size"""
        search_query = {'size': self.startup1_size}
        self.filter_and_assert(search_query, 1)

    def test_get_followed_startups_multiple_filters_positive(self):
        """Test multiple filters in one request"""
        search_query = {'country': self.startup1_country, 'industry': self.startup1_industry}
        self.filter_and_assert(search_query, 1)

    def test_get_followed_startups_multiple_filters_negative(self):
        """Test multiple filters in one request"""
        search_query = {'country': self.startup1_country, 'industry': 'abc'}
        self.filter_and_assert(search_query, 0)

    def tearDown(self):
        del self.token_user3
        self.investor.followed_startups.remove(self.startup1, self.startup2)
        InvestorProfile.objects.all().delete()
        StartupProfile.objects.all().delete()
        User.objects.all().delete()
        super().tearDown()
