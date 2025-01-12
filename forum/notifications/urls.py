from django.urls import path
from .views import (
    NotificationMethodView,
    NotificationCategoryView,
    NotificationPreferenceView,
    NotificationListView, 
    NotificationDetailView,
    InvestorNotificationDetailView,
    InvestorNotificationListView
)

app_name = "notifications"

urlpatterns = [
    path(
        "notification-categories/",
        NotificationCategoryView.as_view(),
        name="notification_categories",
    ),
    path(
        "notification-methods/",
        NotificationMethodView.as_view(),
        name="notification_methods",
    ),
    path(
        "user-notification-preferences/",
        NotificationPreferenceView.as_view(),
        name="user_notification_preferences",
    ),
    path('startup/', NotificationListView.as_view(), name='notifications'),
    path('startup/<int:id>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('investor/', InvestorNotificationListView.as_view(), name='investor_notifications'),
    path('investor/<int:id>/', InvestorNotificationDetailView.as_view(), name='investor_notification_detail'),
]