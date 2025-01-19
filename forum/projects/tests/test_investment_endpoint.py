from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth import get_user_model

from .factories import (
    UserFactory,
    StartupProfileFactory,
    InvestorProfileFactory,
    ProjectFactory
)
from projects.models import Investment
from users.models import Role

User = get_user_model()


class InvestmentCreateEndpointTest(APITestCase):
    """
    Test suite for the Investment creation endpoint.

    This test suite verifies the behavior of the endpoint that allows
    authenticated investors to create investments for specific projects.

    Test scenarios include:
    - Successful investment creation.
    - Handling of completed projects (investments should not be allowed).
    - Ensuring that unauthenticated users cannot create investments.
    - Test for checking validation of funding investments.
    - Checking for exceeding funding goal
    - Checking that non investor cannot invest to the project
    - Invalid project investment creation.
    """

    def setUp(self):
        self.startup_user = UserFactory()
        self.startup_user.role = Role.STARTUP.value
        self.startup_user.save()
        self.startup = StartupProfileFactory(user=self.startup_user)
        self.investor_user = UserFactory()
        self.investor_user.role = Role.INVESTOR.value
        self.investor_user.save()
        self.investor = InvestorProfileFactory(user=self.investor_user)

        self.project = ProjectFactory(
            startup=self.startup,
            funding_goal=Decimal("100.00"),
            is_completed=False
        )
        
        self.client.force_authenticate(user=self.investor_user)
        self.url = reverse('projects:project-investment', kwargs={'project_id': self.project.id})

    def test_create_investment_success(self):
        """Test successful investment creation"""
        data = {"share": "50.00"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Investment.objects.filter(project=self.project, investor=self.investor).exists())

    def test_create_investment_for_completed_project(self):
        """Test investment creation for completed project"""
        self.project.is_completed = True
        self.project.save()
        data = {"share": "50.00"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_investment_unauthenticated(self):
        """Test investment creation by unauthenticated user"""
        self.client.force_authenticate(user=None)
        data = {"share": "50.00"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_investment_as_non_investor(self):
        """Test that a user without investor profile cannot create investments"""
        self.investor.delete()
        self.investor_user.role = Role.STARTUP.value
        self.investor_user.save()
        
        data = {"share": "50.00"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_investment_invalid_project(self):
        """Test investment creation for non-existent project"""
        url = reverse('projects:project-investment', kwargs={"project_id": 9999})
        data = {"share": "50.00"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_completion_after_investment(self):
        """Test that project is marked as completed after full investment"""
        data = {"share": "100.00"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_completed)

    def test_create_investment_exceeding_funding_goal(self):
        """Test investment creation with share exceeding funding goal"""
        data = {"share": "120.00"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_investment_with_invalid_share(self):
        """Test investment creation with invalid share amount"""
        data = {"share": "0.00"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("share", response.data)
        self.assertEqual(response.data["share"][0], "Share must be greater than zero.")
