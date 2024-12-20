from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import StartupProfile
from .serializers import StartupProfileSerializer


class StartupProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def check_owner(self, request, message):
        startup_instance = self.get_object()
        if startup_instance.user != request.user:
            raise PermissionDenied(f"{message}")

    def update(self, request, *args, **kwargs):
        # Restrict PUT to the owner
        message = 'You do not have permission to edit this profile.'
        self.check_owner(request, message)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Restrict PATCH to the owner
        message = 'You do not have permission to edit this profile.'
        self.check_owner(request, message)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Restrict DELETE to the owner
        message = 'You do not have permission to delete this profile.'
        self.check_owner(request, message)
        return super().update(request, *args, **kwargs)