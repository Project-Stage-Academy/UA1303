from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from profiles.models import StartupProfile

User = get_user_model()


class PublicStartupTestCase(APITestCase):

    get_public_startups_url = 'profiles:public-startups-list'
    pagination_page_size = 50

    @classmethod
    def setUpTestData(cls):
        for i in range(cls.pagination_page_size+1):
            user = User.objects.create_user(password=f'password{i}', email=f'user{i}@email.com')
            StartupProfile.objects.create(
                user=user,
                company_name=f'SuperCompany {user}',
                industry='transport',
                size='100',
                country='USA',
                city='Los Angeles',
                zip_code='2000',
                address='Some street 7',
                phone=f'+3806322255{i:02}',
                email=f'random{user}@email.com',
                description='Some description',
                is_public=True,
            )

    def test_public_startups(self):
        """Test public startups GET method. And tests correct fields are present in the response"""
        url = reverse(self.get_public_startups_url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('results'), '"results" not found in data')

        for startup in response.data.get('results'):
            self.assertIn('id', startup, '"id" not found in startup data')
            self.assertIn('company_name', startup,  '"company_name" not found in startup data')
            self.assertIn('industry', startup,  '"industry" not found in startup data')
            self.assertIn('country', startup,  '"country" not found in startup data')
            self.assertIn('city', startup,  '"city" not found in startup data')
            self.assertIn('description', startup, '"description" not found in startup data')

            self.assertNotIn('user', startup)
            self.assertNotIn('size', startup)
            self.assertNotIn('zip_code', startup)
            self.assertNotIn('address', startup)
            self.assertNotIn('phone', startup)
            self.assertNotIn('email', startup)
            self.assertNotIn('is_public', startup)
            self.assertNotIn('created_at', startup)
            self.assertNotIn('updated_at', startup)
            self.assertNotIn('projects', startup)

    def assert_pagination_fields(self, response):
        """Helper method to check pagination fields present in the response"""
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_pagination_first_page(self):
        """Test that the first page contains the correct results."""
        url = reverse(self.get_public_startups_url)
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_pagination_fields(response)

        self.assertEqual(len(response.data.get('results')), self.pagination_page_size)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_pagination_last_page(self):
        """Test that the last page contains the correct results."""
        url = reverse(self.get_public_startups_url)
        response = self.client.get(url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_pagination_fields(response)

        self.assertLessEqual(len(response.data['results']), self.pagination_page_size)
        self.assertIsNotNone(response.data['previous'])
        self.assertIsNone(response.data['next'])

    def test_pagination_non_existing_page(self):
        """Test that pagination does not return the page that doesn't exist."""
        url = reverse(self.get_public_startups_url)
        response = self.client.get(url, {'page': 3})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_results(self):
        """Test that endpoints with no results returns an empty list"""
        StartupProfile.objects.all().update(is_public=False)
        url = reverse(self.get_public_startups_url)
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 0)
