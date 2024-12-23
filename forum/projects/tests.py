from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Project, Description
from profiles.models import StartupProfile

User = get_user_model()


class ProjectTestCase(APITestCase):
    def setUp(self):

        # Creating users. User1 is startup owner who is creating projects.
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

        # Create project for user1
        self.project1 = Project.objects.create(
            title='Test Project',
            funding_goal='10000',
            is_published=False,
            startup_id=self.startup1.pk,
        )

    def get_jwt_token(self, user):
        """Helper method to create a JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_anonymous_project_request(self):
        """Test that user can't access the protected endpoint without login."""
        url = reverse('projects:projects-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_project_request(self):
        """Test that authenticated user can access the protected endpoint"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_project_with_description(self):
        """Test that user can create a new project with description"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': 'my description',
            'title': 'Test Project 2',
            'funding_goal': '20000',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['startup'], self.startup1.pk)

    def test_create_project_without_description(self):
        """Test that user can create a new project without description"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'title': 'Test Project 2',
            'funding_goal': '20000',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['startup'], self.startup1.pk)

    def test_create_project_without_description_field(self):
        """Test that user can create a new project without description field"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'title': 'Test Project 2',
            'funding_goal': '20000',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['startup'], self.startup1.pk)

    def test_create_project_invalid_title(self):
        """Test that user cannot create a new project with invalid title"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'title': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean ms',
            'funding_goal': '20000',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_project_varchar_funding_goal(self):
        """Test that user cannot create a new project with invalid funding goal"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'title': 'Test Project 2',
            'funding_goal': 'asd',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_project_long_funding_goal(self):
        """Test that user cannot create a new project with long funding goal"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'title': 'Test Project 2',
            'funding_goal': '2222222222222222',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_project_negative_funding_goal(self):
        """Test that user cannot create a new project with negative funding goal"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'title': 'Test Project 2',
            'funding_goal': '-10',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_project_missing_title(self):
        """Test that user cannot create a new project with missing title"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'funding_goal': '10000',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_project_missing_funding_goal(self):
        """Test that user cannot create a new project with missing funding goal"""
        url = reverse('projects:projects-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'description': '',
            'title': 'Test Project 2',
            'is_published': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_partial_update_project(self):
        """Test for user to update existing project"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            'title': 'Test Project Updated',
            'funding_goal': '20000',
            'is_published': True,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.title, 'Test Project Updated')
        self.assertEqual(self.project1.is_published, True)

    def test_update_description(self):
        """Test for user to update description in project"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "description": "updated description",
            "title": "Test Project",
            "funding_goal": "10000",
            "is_published": False
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.description.description, 'updated description')

    def test_update_startup_id(self):
        """Test for user to block updating startup_id in project"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        startup = self.project1.startup
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "description": "updated description",
            "title": "Test Project",
            "funding_goal": "10000",
            "is_published": False,
            "startup": 5
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.startup, startup)

    def test_update_completed(self):
        """Test for user to block updating is_completed in project"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        project_completed = self.project1.is_completed
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "description": "updated description",
            "title": "Test Project",
            "funding_goal": "10000",
            "is_published": False,
            "is_completed": True
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.is_completed, project_completed)

    def test_update_project_restricted(self):
        """Test that user cannot update project if not owner"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        data = {
            "description": "updated description",
            "title": "Test Project",
            "funding_goal": "10000",
            "is_published": False
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_restricted(self):
        """Test for user to protect projects from deletion if user is not a project owner"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project(self):
        """Test for user to delete project if user is a project owner"""
        url = reverse('projects:projects-detail', kwargs={'pk': self.project1.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=self.project1.pk).exists())
