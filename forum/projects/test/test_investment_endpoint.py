from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from .factories import (
    UserFactory,
    StartupProfileFactory,
    InvestorProfileFactory,
    ProjectFactory
)
from projects.models import Investment


class InvestmentCreateEndpointTest(APITestCase):
    """
    Test suite for the Investment creation endpoint.

    This test suite verifies the behavior of the endpoint that allows
    authenticated investors to create investments for specific projects.

    Test scenarios include:
    - Successful investment creation.
    - Handling of completed projects (investments should not be allowed).
    - Ensuring that unauthenticated users cannot create investments.
    """

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('password')
        self.user.save()
        self.startup = StartupProfileFactory(user=self.user)
        self.investor = InvestorProfileFactory(user=self.user)
        self.project = ProjectFactory(
            startup=self.startup,
            funding_goal=Decimal("100.00"),
            is_completed=False
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('projects:project-investment', kwargs={'project_id': self.project.id})

    def test_create_investment_success(self):
        url = reverse('projects:project-investment', kwargs={"project_id": self.project.id})
        data = {"share": "50.00"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Investment.objects.filter(project=self.project, investor=self.investor).exists())

    def test_create_investment_for_completed_project(self):
        self.project.is_completed = True
        self.project.save()
        data = {"share": Decimal("50.00")}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_investment_unauthenticated(self):
        self.client.logout()
        data = {"share": Decimal("50.00")}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
