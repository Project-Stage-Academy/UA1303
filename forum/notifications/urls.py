from django.urls import path

from .views import (
    NotificationMethodView,
    NotificationCategoryView,
    NotificationPreferenceView,
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
]
