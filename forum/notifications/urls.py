from django.urls import path
from .views import (
    NotificationTypeView, 
    NotificationPreferenceView, 
    NotificationListView, 
    NotificationDetailView
)

app_name = 'notifications'

urlpatterns = [
    path('notification-types/',
         NotificationTypeView.as_view(),
         name='notification_types'
         ),
    path(
        'user-notification-preferences/',
        NotificationPreferenceView.as_view(),
        name='user_notification_preferences'
    ),
    path('startup/', NotificationListView.as_view(), name='notifications'),
    path('startup/<int:id>/', NotificationDetailView.as_view(), name='notification_detail'),
]