import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Role

from .models import NotificationCategory, NotificationMethod, NotificationPreference
from .serializers import (
    NotificationCategorySerializer,
    NotificationMethodSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer,
)

logger = logging.getLogger(__name__)


PREFERENCE_RESPONSES = {
    200: openapi.Response(
        description="Successful operation", schema=NotificationPreferenceSerializer
    ),
    404: openapi.Response(description="Preferences not found."),
    400: openapi.Response(description="Invalid data."),
}

ROLE_CATEGORIES = {
    Role.STARTUP: ["message", "follow", "subscription"],
    Role.INVESTOR: ["message", "project_changes"],
}

NOTIFICATION_METHODS_RESPONSES = {
    200: openapi.Response(
        description="Successful operation",
        schema=NotificationMethodSerializer(many=True),
    ),
}

NOTIFICATION_CATEGORIES_RESPONSES = {
    200: openapi.Response(
        description="Successful operation",
        schema=NotificationCategorySerializer(many=True),
    ),
    403: openapi.Response(
        description="Invalid role",
        schema=NotificationCategorySerializer(many=True),
    ),
}


class NotificationMethodView(APIView):
    """
    API view to retrieve all available notification methods.

    This view handles the retrieval of notification methods,
    providing details such as the name and description of each method.

    HTTP Methods:
    - GET: Returns a list of all notification methods.

    Responses:
    - 200 OK: A JSON array of notification methods, each with the fields:
        - id (int): The unique identifier of the notification method.
        - name (str): The name of the notification method.
        - description (str): A brief description of the notification method.

    Authorization:
    - Requires the user to be authenticated.
    """

    format_suffix_kwarg = None
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all notification methods.",
        responses=NOTIFICATION_METHODS_RESPONSES,
    )
    def get(self, request):
        notification_methods = NotificationMethod.objects.all()
        serializer = NotificationMethodSerializer(notification_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationCategoryView(APIView):
    """
    API view to retrieve notification categories based on the user's role.

    This view handles the retrieval of notification categories specific
    to the authenticated user's role, providing details such as the name
    and description of each category.

    User roles and their corresponding categories:
    - Role 1 (Startup): Returns categories defined in ROLE_CATEGORIES.
    - Role 2 (Investor): Returns categories defined in ROLE_CATEGORIES.

    HTTP Methods:
    - GET: Retrieves notification categories for the authenticated user.

    Responses:
    - 200 OK: A JSON array of notification categories filtered by the user's role.
        Each category contains:
            - id (int): The unique identifier of the notification category.
            - name (str): The name of the notification category.
            - description (str): A brief description of the notification
            category.

    Authorization:
    - Requires the user to be authenticated via JWT.
    - Role information is extracted from the JWT token's "role" claim.
    """

    format_suffix_kwarg = None
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all notification categories for current role.",
        responses=NOTIFICATION_CATEGORIES_RESPONSES,
    )
    def get(self, request):
        role = request.auth.get("role")
        notification_categories = NotificationCategory.objects.filter(
            name__in=ROLE_CATEGORIES.get(role, [])
        )
        serializer = NotificationCategorySerializer(notification_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationPreferenceView(APIView):
    """
    API view to manage the notification preferences of the authenticated
    user.

    This view allows users to retrieve, update, and delete their
    notification preferences for current role.

    Permissions:
    - Requires authentication (`IsAuthenticated`).
    - Preferences will be displayed and can be modified depends
    on the current role.

    HTTP Methods:
    - GET: Retrieve the user's current role notification preferences.
    - PUT: Update or create the user's current role notification preferences.
    - DELETE: Delete the current user's notification preferences.

    Responses:
    - 200 OK: The operation was successful.
    - 400 Bad Request: The request data is invalid or missing.
    - 400 Bad Request: You cant change some categories with current role..
    - 404 Not Found: No notification preferences are set for the user.
    - 500 Internal Server Error: An unexpected error occurred.
    """

    format_suffix_kwarg = None
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the current user's notification preferences.",
        responses=PREFERENCE_RESPONSES,
    )
    def get(self, request):
        preferences = NotificationPreference.objects.filter(user=request.user).first()

        if preferences:
            logger.info(f"Preferences retrieved for user {request.user.email}")
            serializer = NotificationPreferenceSerializer(preferences)
            data = self._filter_categories_dict_by_role(request, serializer.data)
            return Response(data, status=status.HTTP_200_OK)

        logger.warning(f"No preferences found for user {request.user.email}")
        return Response(
            {"detail": "Notification preferences not set."},
            status=status.HTTP_404_NOT_FOUND,
        )

    @swagger_auto_schema(
        operation_description="Update the current user's notification preferences.",
        request_body=NotificationPreferenceUpdateSerializer,
        responses=PREFERENCE_RESPONSES,
    )
    def put(self, request):
        if not request.data:
            return Response(
                {"detail": "No data provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not self._check_update_possibility(request):
            return Response(
                {"detail": "You cant change some categories with current role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preferences = NotificationPreference.objects.get_or_create(user=request.user)[0]
        data = self._update_categories_dict(request, preferences)
        serializer = NotificationPreferenceUpdateSerializer(preferences, data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"Preferences updated for user {request.user.email}")
                return Response(
                    {"detail": "Notification preferences updated successfully."},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(
                    f"Error updating preferences for user {request.user.email}: {str(e)}"
                )
                return Response(
                    {"detail": "An error occurred while updating preferences."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        logger.error(
            f"Invalid data provided for user {request.user.email}: {serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Deletes the current user's preference for both roles."
    )
    def delete(self, request):
        preferences = NotificationPreference.objects.filter(user=request.user)
        if preferences:
            preferences.delete()
            logger.info(f"Preferences deleted for user {request.user.email}")
            return Response(
                {"detail": "Notification preferences deleted successfully."},
                status=status.HTTP_200_OK,
            )
        logger.warning(
            f"Attempted to delete preferences for non-existent user {request.user.email}"
        )
        return Response(
            {"detail": "Notification preferences not set."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def _update_categories_dict(self, request, preference_instance):
        """
        Helper method for PUT HTTP. Allows change categories related
        to current role and do not rewrite another role categories
        at the same time. Returns dict which can be serilized.
        """

        role = request.auth.get("role")
        current_data = request.data.copy()
        serializer = NotificationPreferenceSerializer(preference_instance)
        current_categories = serializer.data["allowed_notification_categories"]
        new_categories = [
            category["id"]
            for category in current_categories
            if category["name"] not in ROLE_CATEGORIES.get(role, [])
        ]
        new_categories += request.data["allowed_notification_categories"]
        current_data["allowed_notification_categories"] = new_categories
        return current_data

    def _filter_categories_dict_by_role(self, request, preference_dict):
        """
        Helper method for GET HTTP. Allows to show categories in preference
        related to the current role. Returns dict which can be serilized.
        """

        role = request.auth.get("role")
        preference_data = preference_dict.copy()
        preference_data["allowed_notification_categories"] = [
            category
            for category in preference_data["allowed_notification_categories"]
            if category["name"] in ROLE_CATEGORIES.get(role, [])
        ]
        return preference_data

    def _check_update_possibility(self, request):
        """
        Helper method for PUT HTTP. Allows you to check if the
        categories to be modified match this role. Returns True or False
        """

        role = request.auth.get("role")
        categories_to_modify = ROLE_CATEGORIES.get(role, [])
        request_categories = request.data.get("allowed_notification_categories")
        request_categories = [
            NotificationCategory.objects.get(id=category).name
            for category in request_categories
        ]
        return all(category in categories_to_modify for category in request_categories)
