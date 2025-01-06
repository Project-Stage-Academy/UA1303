from django.urls import path

from .views import (
    NotificationMethodView,
    NotificationCategoryView,
    NotificationPreferenceView,
    InvestorNotificationListView,
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
    path(
        "investor-notifications/",
        InvestorNotificationListView.as_view(),
        name="investor_notifications/",
    ),
]
