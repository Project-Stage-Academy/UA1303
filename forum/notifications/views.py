import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import generics
from rest_framework import exceptions
from .models import StartUpNotification
from .serializers import StartUpNotificationReadSerializer
from .paginations import StandardResultsSetPagination
from .permissions import HasStartupProfilePermission, HasStartupAccessPermission
from rest_framework import generics

from .models import NotificationMethod, NotificationPreference, NotificationCategory
from .serializers import (
    NotificationMethodSerializer,
    NotificationCategorySerializer,
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
    """

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
    API view to retrieve all available notification categories.

    This view handles the retrieval of notification categories,
    providing details such as the name and description of each category.

    HTTP Methods:
    - GET: Returns a list of all notification categories.

    Responses:
    - 200 OK: A JSON array of notification categories, each with the fields:
        - id (int): The unique identifier of the notification category.
        - name (str): The name of the notification category.
        - description (str): A brief description of the notification category.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all notification categories.",
        responses=NOTIFICATION_CATEGORIES_RESPONSES,
    )
    def get(self, request):
        notification_categories = NotificationCategory.objects.all()
        serializer = NotificationCategorySerializer(notification_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationPreferenceView(APIView):
    """
    API view to manage the notification preferences of the authenticated
    user.

    This view allows users to retrieve, update, and delete their
    notification preferences.

    Permissions:
    - Requires authentication (`IsAuthenticated`).

    HTTP Methods:
    - GET: Retrieve the current user's notification preferences.
    - PUT: Update or create the current user's notification preferences.
    - DELETE: Delete the current user's notification preferences.

    Responses:
    - 200 OK: The operation was successful.
    - 400 Bad Request: The request data is invalid or missing.
    - 404 Not Found: No notification preferences are set for the user.
    - 500 Internal Server Error: An unexpected error occurred.
    """

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
            return Response(serializer.data, status=status.HTTP_200_OK)
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

        preferences = NotificationPreference.objects.get_or_create(user=request.user)[0]
        serializer = NotificationPreferenceUpdateSerializer(
            preferences, data=request.data
        )

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


class NotificationListView(generics.ListAPIView):
    """
    To get all notifications as a list of dicts
    """
    permission_classes = [IsAuthenticated, HasStartupProfilePermission]
    pagination_class = StandardResultsSetPagination
    serializer_class = StartUpNotificationReadSerializer

    def get_queryset(self):
        startup_id = self.request.user.startup_profile.id
        return StartUpNotification.objects.filter(startup_id=startup_id).order_by('id').select_related('notification_category', 'investor', 'startup')

    def get_serializer_context(self):
        return {'request': self.request}
    

class NotificationDetailView(generics.RetrieveAPIView):
    """
    To get a single notification and set 'is_read' to True
    """
    permission_classes = [IsAuthenticated, HasStartupProfilePermission, HasStartupAccessPermission]
    queryset = StartUpNotification.objects.all()
    serializer_class = StartUpNotificationReadSerializer
    lookup_field = 'id'

    def get_object(self):
        notification = super().get_object()
        notification.mark_as_read()
        return notification
    
    def get_serializer_context(self):
        return {'request': self.request}