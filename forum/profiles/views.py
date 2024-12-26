from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from .models import InvestorProfile
from .models import StartupProfile
from .permissions import IsOwnerOrReadOnly
from .serializers import InvestorProfileSerializer
from .serializers import StartupProfileSerializer


class InvestorViewSet(ModelViewSet):
    """
    API Endpoint for Investor Profiles
    """
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return InvestorProfile.objects.filter(user=self.request.user).select_related(
                "user"
            )
        return InvestorProfile.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StartupProfileViewSet(ModelViewSet):
    """
    API Endpoint for Startup Profiles
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['company_name', 'industry', 'country', 'city']
    filterset_fields = ['industry', 'country', 'city', 'size']
    ordering_fields = ['company_name', 'created_at']

    def perform_create(self, serializer):
        """Automatically assigns startup profile to the right user based on user's token"""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="The list of Startup Profiles",
        operation_description=(
                "Supports the following features:\n\n"
                "**Search**:\n"
                "- `company_name`\n"
                "- `industry`\n"
                "- `country`\n"
                "- `city`\n\n"
                "**Filter**:\n"
                "- `industry`\n"
                "- `country`\n"
                "- `city`\n"
                "- `size`\n\n"
                "**Sort by**:\n"
                "- `company_name`\n"
                "- `created_at`\n\n"
                "Use `-` for descending order (e.g., '-created_at' vs 'created')"
        ),

    )
    def list(self, request, *args, **kwargs):
        """
        Handles GET requests for listing startup profiles.
        """
        return super().list(request, *args, **kwargs)


class SaveStartupViewSet(GenericViewSet):
    """Adds startup to user's favourites"""
    permission_classes = [IsAuthenticated]
    serializer_class = Serializer
    queryset = StartupProfile.objects.all()

    @action(detail=True, methods=['post'], url_path='save', url_name='save')
    def post(self, request, pk):
        investor = get_object_or_404(InvestorProfile, user=request.user)
        startup = get_object_or_404(StartupProfile, pk=pk)
        if startup.followers.filter(pk=investor.pk).exists():
            return Response({'detail': 'Startup is already followed'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.add(investor)
        return Response({'detail': 'Startup is saved'}, status=status.HTTP_200_OK)
