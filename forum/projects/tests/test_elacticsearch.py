# from decimal import Decimal
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from elasticsearch_dsl import connections
# from django.contrib.auth import get_user_model
#
# from projects.tests.factories import ProjectFactory
# from profiles.tests.factories import StartupProfileFactory, InvestorProfileFactory, UserFactory
# from .documents import ProjectDocument, StartupDocument
#
# User = get_user_model()
#
#
# class SearchAPITests(APITestCase):
#     @classmethod
#     def setUpClass(cls):
#         """Set up Elasticsearch connection and create indexes"""
#         super().setUpClass()
#         connections.create_connection(hosts=['localhost'])
#         ProjectDocument._index.delete(ignore=404)
#         ProjectDocument._index.create()
#         StartupDocument._index.delete(ignore=404)
#         StartupDocument._index.create()
#
#     def setUp(self):
#         """Set up test data and authenticate user"""
#         # Create startup user and profile
#         self.startup_user = UserFactory()
#         self.startup_user.role = Role.STARTUP.value
#         self.startup_user.save()
#         self.startup = StartupProfileFactory(
#             user=self.startup_user,
#             company_name="Test Startup",
#             industry="Technology"
#         )
#
#         # Create investor user and profile
#         self.investor_user = UserFactory()
#         self.investor_user.role = Role.INVESTOR.value
#         self.investor_user.save()
#         self.investor = InvestorProfileFactory(user=self.investor_user)
#
#         # Create test projects
#         self.project1 = ProjectFactory(
#             startup=self.startup,
#             title="AI Project",
#             funding_goal=Decimal("100000.00"),
#             is_published=True
#         )
#         self.project2 = ProjectFactory(
#             startup=self.startup,
#             title="Blockchain Project",
#             funding_goal=Decimal("200000.00"),
#             is_published=True
#         )
#
#         # Index documents in Elasticsearch
#         ProjectDocument().update(self.project1)
#         ProjectDocument().update(self.project2)
#         StartupDocument().update(self.startup)
#
#         # Refresh indices
#         ProjectDocument._index.refresh()
#         StartupDocument._index.refresh()
#
#         # Authenticate user
#         self.client.force_authenticate(user=self.investor_user)
#
#         # Set up URLs
#         self.projects_search_url = reverse('projects:project-search')
#         self.startups_search_url = reverse('startups:startup-search')
#
#     def test_search_projects_by_title(self):
#         """Test searching projects by title"""
#         response = self.client.get(
#             self.projects_search_url,
#             {'q': 'AI Project'}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['title'], 'AI Project')
#
#     def test_search_projects_with_filters(self):
#         """Test searching projects with filters"""
#         response = self.client.get(
#             self.projects_search_url,
#             {
#                 'industry': 'Technology',
#                 'is_published': 'true'
#             }
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)  # Both projects should match
#
#     def test_search_projects_sorting(self):
#         """Test searching projects with sorting"""
#         response = self.client.get(
#             self.projects_search_url,
#             {'sort_by': 'funding_goal'}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)
#         self.assertTrue(
#             Decimal(response.data[0]['funding_goal']) <=
#             Decimal(response.data[1]['funding_goal'])
#         )
#
#     def test_search_startups_by_name(self):
#         """Test searching startups by company name"""
#         response = self.client.get(
#             self.startups_search_url,
#             {'q': 'Test Startup'}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['company_name'], 'Test Startup')
#
#     def test_search_startups_with_filters(self):
#         """Test searching startups with filters"""
#         response = self.client.get(
#             self.startups_search_url,
#             {'industry': 'Technology'}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['industry'], 'Technology')
#
#     def test_search_unauthenticated(self):
#         """Test search endpoints with unauthenticated user"""
#         self.client.force_authenticate(user=None)
#
#         response = self.client.get(self.projects_search_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         response = self.client.get(self.startups_search_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_search_with_invalid_params(self):
#         """Test search with invalid parameters"""
#         response = self.client.get(
#             self.projects_search_url,
#             {'invalid_param': 'value'}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)  # Should return all projects
#
#     def test_empty_search_results(self):
#         """Test search with no matching results"""
#         response = self.client.get(
#             self.projects_search_url,
#             {'q': 'NonexistentProject'}
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)
#
#     @classmethod
#     def tearDownClass(cls):
#         """Clean up Elasticsearch indices"""
#         super().tearDownClass()
#         ProjectDocument._index.delete(ignore=404)
#         StartupDocument._index.delete(ignore=404)
