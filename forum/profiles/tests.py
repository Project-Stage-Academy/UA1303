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
