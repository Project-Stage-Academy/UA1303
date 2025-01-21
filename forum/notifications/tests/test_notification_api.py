from rest_framework import status
from rest_framework.test import APITestCase
from ..factories import InvestorProfileFactory, StartupProfileFactory
from django.urls import reverse

from .test_notificationpreference import generate_auth_header
from users.serializers import create_default_notification_preferences


class NotificationsAPITests(APITestCase):
    """
    Integration tests for the notification API.

    This class contains tests for the end-to-end workflow of the notification system,
    including testing user notification preferences and startup/investor notifications.
    """

    def follow_startup(self, startup, startup_header, investors_headers: tuple):
        url = reverse('profiles:startups-save-favorite', kwargs={'pk': startup.pk})
        for investor_header in investors_headers:
            response = self.client.post(url, **investor_header)
            self.assertIn('is saved', response.json()['detail'])

        url = reverse('notifications:startup_notifications')
        response = self.client.get(url, **startup_header)
        return response


    @classmethod
    def setUpTestData(cls):
        cls.investor_1 = InvestorProfileFactory()
        cls.investor_2 = InvestorProfileFactory()
        cls.startup = StartupProfileFactory()

        create_default_notification_preferences(cls.startup.user)
        create_default_notification_preferences(cls.investor_1.user)
        create_default_notification_preferences(cls.investor_2.user)

        cls.auth_header_startup = generate_auth_header(cls.startup.user, 1)
        cls.auth_header_investor_1 = generate_auth_header(cls.investor_1.user, 2)
        cls.auth_header_investor_2 = generate_auth_header(cls.investor_2.user, 2)

        cls.project_info = {
            "description": "TEST",
            "title": "TEST",
            "funding_goal": "10000",
            "is_published": True
        }


    def test_startup_follow_notifications(self):        
        """
        Test the notification flow when investors follow a startup.
        Tests how 'follow' signals behave with different notification preferences.
        
        Verifies:
        1. Follow notifications are enabled by default
        2. Startup receives notification when followed
        3. Notification count increases appropriately
        4. Disabling notifications prevents new follow notifications
        """
        url = reverse('notifications:user_notification_preferences')
        response = self.client.get(url, **self.auth_header_startup)
        self.assertIn('follow', [category['name'] for category in response.json()['allowed_notification_categories']])

        url = reverse('profiles:startups-save-favorite', kwargs={'pk': self.startup.pk})
        response = self.client.post(url, **self.auth_header_investor_1)
        self.assertIn('is saved', response.json()['detail'])

        url = reverse('notifications:startup_notifications')
        response = self.client.get(url, **self.auth_header_startup)
        self.assertEqual(response.json()['count'], 1, "Expected 1 notification.")

        body = {
            "allowed_notification_methods": [1, 2],
            "allowed_notification_categories": []
        }
        url = reverse('notifications:user_notification_preferences')
        response = self.client.put(url, body, format='json', **self.auth_header_startup)
        self.assertEqual(response.json(), {'detail': 'Notification preferences updated successfully.'})

        url = reverse('profiles:startups-save-favorite', kwargs={'pk': self.startup.pk})
        response = self.client.post(url, **self.auth_header_investor_2)

        url = reverse('notifications:startup_notifications')
        response = self.client.get(url, **self.auth_header_startup)
        self.assertEqual(response.json()['count'], 1, "Expected 1 notification.")
    
    
    def test_startup_update_notifications(self):
        """
        Test notifications sent when a startup updates their profile.
        Tests how 'profile_update' signals behave with different notification preferences.
        
        Verifies:
        1. Followers receive notifications for profile updates
        2. Notification preferences affect update notifications
        3. Only followers with enabled preferences receive updates
        4. Notification counts are accurate after preferences change
        """
        response = self.follow_startup(
            self.startup,
            self.auth_header_startup,
            (self.auth_header_investor_1, self.auth_header_investor_2)
        )
        self.assertEqual(response.json()['count'], 2, "Expected 2 notifications.")

        body = {
            "allowed_notification_methods": [1, 2],
            "allowed_notification_categories": []
        }
        url = reverse('notifications:user_notification_preferences')
        response = self.client.put(url, body, format='json', **self.auth_header_investor_1)
        self.assertEqual(response.json(), {'detail': 'Notification preferences updated successfully.'})

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup.pk})
        response = self.client.get(url, **self.auth_header_startup)

        update_data = {
            **response.json(),
            "phone": "+380987654321"
        }
        response = self.client.put(url, update_data, format='json', **self.auth_header_startup)   
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['phone'], "+380987654321")

        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, **self.auth_header_investor_1)
        self.assertEqual(response.json()['count'], 0, "Expected 0 notifications.")
        response = self.client.get(url, **self.auth_header_investor_2)
        self.assertEqual(response.json()['count'], 1, "Expected 1 notification.")


    def test_new_project_notifications(self):
        """
        Test notifications sent when a startup creates new projects.
        Tests how 'new_project' signals behave with different notification preferences.
        
        Verifies:
        1. Followers receive notifications for new projects
        2. Notification preferences affect project notifications
        3. Multiple projects generate multiple notifications
        4. Notification counts are accurate after preferences change
        """
        response = self.follow_startup(
            self.startup,
            self.auth_header_startup,
            (self.auth_header_investor_1, self.auth_header_investor_2)
        )
        self.assertEqual(response.json()['count'], 2, "Expected 2 notifications.")

        url = reverse('projects:projects-list')
        response = self.client.post(url, self.project_info, format='json', **self.auth_header_startup)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        body = {
            "allowed_notification_methods": [1, 2],
            "allowed_notification_categories": []
        }
        url = reverse('notifications:user_notification_preferences')
        response = self.client.put(url, body, format='json', **self.auth_header_investor_1)
        self.assertEqual(response.json(), {'detail': 'Notification preferences updated successfully.'})

        url = reverse('projects:projects-list')
        self.project_info['title'] = "Second project"
        response = self.client.post(url, self.project_info, format='json', **self.auth_header_startup)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, **self.auth_header_investor_1)
        self.assertEqual(response.json()['count'], 1, "Expected 1 notification.")
        response = self.client.get(url, **self.auth_header_investor_2)
        self.assertEqual(response.json()['count'], 2, "Expected 2 notifications.")
        

    def test_in_app_preference(self):
        """
        Test that in-app notification preferences are properly handled when:
        1. A startup is followed by multiple investors
        2. Investor 1 excludes 'in_app' preference
        3. The notification system tracks that preference correctly for the investor
        4. Investor 2 still receives the notification
        """
        response = self.follow_startup(
            self.startup,
            self.auth_header_startup,
            (self.auth_header_investor_1, self.auth_header_investor_2)
        )
        
        body = {
            "allowed_notification_methods": [1],
            "allowed_notification_categories": [2, 3]
        }
        url = reverse('notifications:user_notification_preferences')
        response = self.client.put(url, body, format='json', **self.auth_header_investor_1)
        self.assertEqual(response.json(), {'detail': 'Notification preferences updated successfully.'})

        url = reverse('projects:projects-list')
        response = self.client.post(url, self.project_info, format='json', **self.auth_header_startup)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, **self.auth_header_investor_1)
        self.assertEqual(response.json()['count'], 0, "Expected 0 notifications.")
        response = self.client.get(url, **self.auth_header_investor_2)
        self.assertEqual(response.json()['count'], 1, "Expected 1 notification.")