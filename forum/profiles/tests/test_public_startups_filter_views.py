from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from profiles.models import StartupProfile
from faker import Faker


User = get_user_model()
fake = Faker()


class PublicStartupFilterTestCase(APITestCase):
    def setUp(self):
        StartupProfile.objects.all().delete()
        self.url = reverse('profiles:public-startup-filter-list')

        self.startups = []
        for i in range(15):
            user = User.objects.create_user(
                email=fake.email(),
                password=fake.password(
                    length=10,
                    special_chars=True,
                    upper_case=True,
                    lower_case=True
                )
            )
            startup = StartupProfile.objects.create(
                user=user,
                company_name=f"Test Company {i}",
                industry=fake.random_element(["Technology", "Healthcare", "Finance"]),
                size=fake.random_element(["100", "200", "300"]),
                country=fake.random_element(["USA", "Canada", "Germany"]),
                city=fake.random_element(["New York", "Toronto", "Berlin"]),
                zip_code=fake.zipcode(),
                email=fake.email(),
                is_public=True
            )

            self.startups.append(startup)

    def test_list_all_startups(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 15)

    def test_filter_by_industry(self):
        response = self.client.get(self.url, {"industry": "Technology"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data:
            self.assertEqual(startup["industry"], "Technology")
    
    def test_filter_by_country(self):
        response = self.client.get(self.url, {"country": "USA"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data:
            self.assertEqual(startup["country"], "USA")
    
    def test_filter_by_city(self):
        response = self.client.get(self.url, {"city": "Toronto"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data:
            self.assertEqual(startup['city'], "Toronto")
    
    def test_search_by_company_name(self):
        response = self.client.get(self.url, {'search': 'Test Company 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data:
            self.assertIn('Test Company 1', startup['company_name'])

    def test_ordering_by_company_name(self):
        response = self.client.get(self.url, {'ordering': "company_name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_names = [startup['company_name'] for startup in response.data]
        self.assertEqual(company_names, sorted(company_names))

    def test_return_empty_list(self):
        response = self.client.get(self.url, {'industry': "IT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def tearDown(self):
        StartupProfile.objects.all().delete()