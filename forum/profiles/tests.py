from django.test import TestCase
from rest_framework.test import APITestCase
from .models import InvestorProfile
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import InvestorProfileSerializer

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


        self.invalid_balance_data_smaller_balance = {
            "country": "Ukraine",
            "city": "Lviv",
            "zip_code": "79000",
            "address": "Shevchenka St. 25",
            "phone": "+380991234567",
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
            "account_balance": 999999*999999,
        }

    def test_create_investor_profile(self):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_create_investor_profile(self):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, self.invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_investor_profile_missing_email(self):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, self.missing_email_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_create_investor_profile_invalid_phone(self):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, self.invalid_phone_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

    def test_create_investor_profile_invalid_balance_bigger(self):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, self.invalid_balance_data_bigger_balance, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account_balance", response.data)

    def test_create_investor_profile_invalid_balance_smaller(self):
        url = reverse("profiles:investor-profile-list")
        response = self.client.post(url, self.invalid_balance_data_smaller_balance, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account_balance", response.data)    

    def tearDown(self):
        del self.user
        del self.token
