from django.urls import path

from .views import (
    NotificationTypeView,
    NotificationCategoryView,
    NotificationPreferenceView
)

app_name = 'notifications'

urlpatterns = [
    path('notification-categories/',
         NotificationCategoryView.as_view(),
         name='notification_categories'
         ),
    path('notification-types/',
         NotificationTypeView.as_view(),
         name='notification_types'
         ),
    path(
        'user-notification-preferences/',
        NotificationPreferenceView.as_view(),
        name='user_notification_preferences'
    ),
]
