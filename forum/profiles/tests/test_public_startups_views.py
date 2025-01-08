from faker import Faker
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from profiles.models import StartupProfile

User = get_user_model()
fake = Faker()


class PublicStartupTestCase(APITestCase):
    def setUp(self):
        User.objects.all().delete()
        StartupProfile.objects.all().delete()
        self.url = reverse('profiles:public-startups-list')

        self.startups = []
        for i in range(55):
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
    
    def test_list_all_statrtups(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 50)
        self.assertEqual((response.data['count']), 55)

    def test_pagination_first_page(self):
        response = self.client.get(self.url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 50)
        self.assertEqual((response.data['count']), 55)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_pagination_last_page(self):
        response = self.client.get(self.url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual((response.data['count']), 55)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_invalid_page(self):
        response = self.client.get(self.url, {'page': 999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_industry(self):
        response = self.client.get(self.url, {"industry": "Technology"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data['results']:
            self.assertEqual(startup['industry'], 'Technology')

    def test_filter_by_country(self):
        response = self.client.get(self.url, {"country": "USA"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data['results']:
            self.assertEqual(startup["country"], "USA")
    
    def test_filter_by_city(self):
        response = self.client.get(self.url, {"city": "Toronto"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data['results']:
            self.assertEqual(startup['city'], "Toronto")

    def test_search_by_company_name(self):
        response = self.client.get(self.url, {'search': 'Test Company 49'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data['results']:
            self.assertIn('Test Company 49', startup['company_name'])

    def test_ordering_by_company_name(self):
        response = self.client.get(self.url, {'ordering': "company_name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_names = [startup['company_name'] for startup in response.data['results']]
        self.assertEqual(company_names, sorted(company_names))

    def test_return_empty_list(self):
        response = self.client.get(self.url, {'industry': "IT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_filter_and_ordering(self):
        response = self.client.get(self.url, {'industry': "Technology", 'ordering': 'company_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        startups = response.data['results']
        self.assertTrue(all(startup['industry'] == 'Technology' for startup in startups))
        company_names = [startup['company_name'] for startup in startups]
        self.assertEqual(company_names, sorted(company_names))

    def test_search_no_results(self):
        response = self.client.get(self.url, {'search': 'Nonexistent Company'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['results'], [])
    
    def test_unauthenticated_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_combined_filters(self):
        response = self.client.get(self.url, {'industry': 'Technology', 'country': 'USA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for startup in response.data['results']:
            self.assertEqual(startup['industry'], 'Technology')
            self.assertEqual(startup['country'], 'USA')

    def tearDown(self):
        User.objects.all().delete()
        StartupProfile.objects.all().delete()
        super().tearDown()