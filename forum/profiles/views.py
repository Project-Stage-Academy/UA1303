from rest_framework.viewsets import ModelViewSet
from .models import InvestorProfile
from .serializers import InvestorProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class InvestorViewSet(ModelViewSet):
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return InvestorProfile.objects.filter(user=user)
        else:
            return InvestorProfile.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            serializer.save(user=user)
        else:
            raise ValueError("User must be authenticated to create an investor profile")

    def check_owner(self, request, message):
        investor_instance = self.get_object()
        if investor_instance.user != request.user:
            raise PermissionDenied(f"{message}")

    def update(self, request, *args, **kwargs):
        # Restrict PUT to the owner
        message = "You do not have permission to edit this profile."
        self.check_owner(request, message)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Restrict PATCH to the owner
        message = "You do not have permission to edit this profile."
        self.check_owner(request, message)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Restrict DELETE to the owner
        message = "You do not have permission to delete this profile."
        self.check_owner(request, message)
        return super().update(request, *args, **kwargs)
