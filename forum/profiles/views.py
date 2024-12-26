from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import InvestorProfile, StartupProfile
from .serializers import InvestorProfileSerializer, StartupProfileSerializer
from .permissions import IsOwnerOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class InvestorViewSet(ModelViewSet):

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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer

    def perform_create(self, serializer):
        """Automatically assigns startup profile to the right user based on user's token"""
        serializer.save(user=self.request.user)


class SaveStartupViewSet(ListModelMixin, GenericViewSet):
    """Managing user's favourite startups"""
    permission_classes = [IsAuthenticated]
    serializer_class = StartupProfileSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ['company_name', 'industry', 'country', 'city']
    filterset_fields = ['industry', 'country', 'city', 'size']
    ordering_fields = ['company_name', 'created_at']

    def get_queryset(self):
        """Returns queryset for current user's saved startups"""
        if self.request.user.is_authenticated:
            investor = get_object_or_404(InvestorProfile, user=self.request.user)
            return investor.followed_startups.all()

    def get_serializer_class(self):
        """Returns the appropriate serializer class based on the action"""
        if self.action == 'save_startup' or self.action == 'delete_favorite':
            return Serializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        tags=['Save Follow Startups'],
        manual_parameters=[
            openapi.Parameter(
                'industry', openapi.IN_QUERY,
                description="Filter by industry",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'country', openapi.IN_QUERY,
                description="Filter by country",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY,
                description="Filter by city",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'size', openapi.IN_QUERY,
                description="Filter by size",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of followed startups"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Save Follow Startups'])
    @action(detail=True, methods=['post'], url_path='save-favorite', url_name='save-favorite')
    def save_startup(self, request, pk):
        """Add a startup to the user's favourites"""
        investor = get_object_or_404(InvestorProfile, user=request.user)
        startup = get_object_or_404(StartupProfile, pk=pk)
        if startup.followers.filter(pk=investor.pk).exists():
            return Response({'detail': 'Startup is already followed'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.add(investor)
        return Response({'detail': 'Startup is saved'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Save Follow Startups'])
    @action(detail=True, methods=['delete'], url_path='delete-favorite', url_name='delete-favorite')
    def delete_favorite(self, request, pk):
        """Remove startup from favorites"""
        investor = get_object_or_404(InvestorProfile, user=request.user)
        startup = get_object_or_404(StartupProfile, pk=pk)
        if not startup.followers.filter(pk=investor.pk).exists():
            return Response({'detail': 'Startup is not in favourites'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.remove(investor)
        return Response({'detail': 'Startup has been removed'}, status=status.HTTP_200_OK)
