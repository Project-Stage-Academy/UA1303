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

from .models import NotificationType, NotificationPreference
from .serializers import (
    NotificationTypeSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer
)

logger = logging.getLogger(__name__)

PREFERENCE_RESPONSES = {
    200: openapi.Response(description="Successful operation", schema=NotificationPreferenceSerializer),
    404: openapi.Response(description="Preferences not found."),
    400: openapi.Response(description="Invalid data."),
}

NOTIFICATION_TYPES_RESPONSES = {
    200: openapi.Response(description="Successful operation", schema=NotificationTypeSerializer(many=True)),
}


class NotificationTypeView(APIView):
    """
    To get all possible Notification Types
    """
    @swagger_auto_schema(
        operation_description="Get all notification types.",
        responses=NOTIFICATION_TYPES_RESPONSES,
    )
    def get(self, request):
        notification_types = NotificationType.objects.all()
        serializer = NotificationTypeSerializer(notification_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationPreferenceView(APIView):
    """
    To get, update or delete a notification preference of the user
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the current user's notification preferences.",
        responses=PREFERENCE_RESPONSES,
    )
    def get(self, request):
        preferences = NotificationPreference.objects.filter(user=request.user).first()
        if preferences:
            logger.info(f"Preferences retrieved for user {request.user.username}")
            serializer = NotificationPreferenceSerializer(preferences)
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.warning(f"No preferences found for user {request.user.username}")
        return Response({"detail": "Notification preferences not set."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update the current user's notification preferences.",
        request_body=NotificationPreferenceUpdateSerializer,
        responses=PREFERENCE_RESPONSES,
    )
    def put(self, request):
        if not request.data:
            return Response({"detail": "No data provided."}, status=status.HTTP_400_BAD_REQUEST)

        preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceUpdateSerializer(preferences, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Preferences updated for user {request.user.username}")
            return Response({"detail": "Notification preferences updated successfully."}, status=status.HTTP_200_OK)
        logger.error(f"Invalid data provided for user {request.user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        preferences = self.get_preference(request.user)
        if preferences:
            preferences.delete()
            logger.info(f"Preferences deleted for user {request.user.username}")
            return Response({"detail": "Notification preferences deleted successfully."}, status=status.HTTP_200_OK)
        logger.warning(f"Attempted to delete preferences for non-existent user {request.user.username}")
        return Response({"detail": "Notification preferences not set."}, status=status.HTTP_404_NOT_FOUND)


class NotificationListView(generics.ListAPIView):
    """
    To get all notifications as a list of dicts
    """
    permission_classes = [IsAuthenticated, HasStartupProfilePermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        startup_id = self.request.user.startup_profile.id
        return StartUpNotification.objects.filter(startup_id=startup_id).order_by('id').select_related('notification_type', 'investor', 'startup')

    serializer_class = StartUpNotificationReadSerializer

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