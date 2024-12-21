from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import StartupProfile

User = get_user_model()


class ProfileTestCase(APITestCase):
    def setUp(self):
        # Creating users. User1 is startup owner.
        self.user1 = User.objects.create_user(username='user1', password='password1', email='user1@email.com')
        self.user2 = User.objects.create_user(username='user2', password='password2', email='user2@email.com')

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

    def test_anonymous_startup_request(self):
        """Test that user can't access the protected endpoint without login."""
        url = reverse('profiles:profiles-list')
        response = self.client.get(url)
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
        self.assertEqual(response.status_code, 201)

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

    def test_delete_startup_profile(self):
        """Test for user to delete startup if user is a startup owner"""
        url = reverse('profiles:profiles-detail', kwargs={'pk': self.startup1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProfile.objects.filter(pk=self.startup1.pk).exists())
