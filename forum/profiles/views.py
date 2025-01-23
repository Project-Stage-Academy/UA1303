from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django_ratelimit.decorators import ratelimit
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import InvestorProfile, StartupProfile
from .permissions import IsOwnerOrReadOnly
from .serializers import InvestorProfileSerializer, StartupProfileSerializer, PublicStartupProfileSerializer
from projects.models import Project


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
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["country", "email"],  # Specify required fields
            properties={
                "country": openapi.Schema(
                    type=openapi.TYPE_OBJECT,  # Because `country_dict=True`
                    description=(
                        "Country input can be either:\n"
                        "- A two-letter country code (ISO 3166-1 alpha-2, e.g., 'US')\n"
                        "- A dictionary with 'code' and 'name' (e.g., {'code': 'US', 'name': 'United States'})"
                    ),
                    example="US",
                ),
                "city": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="City name.",
                    example="San Francisco",
                ),
                "zip_code": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Postal code (must include at least one numeric character).",
                    example="94105",
                ),
                "address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Street address.",
                    example="123 Market Street",
                ),
                "phone": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Phone number (optional).",
                    example="+1 415-555-0123",
                    nullable=True,
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="email",
                    description="Email address (must be unique).",
                    example="investor@example.com",
                ),
                "account_balance": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description=(
                        "Account balance in USD. Must be positive and less than "
                        "9,999,999,999,999.99."
                    ),
                    example=50000.00,
                    minimum=0,
                    maximum=9_999_999_999_999.99,
                ),
            },
        ),
        responses={
            201: openapi.Response("Investor profile created successfully."),
            400: openapi.Response("Validation error."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class StartupProfileViewSet(ModelViewSet):
    """
    API Endpoint for Startup Profiles
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = StartupProfile.objects.all().order_by('company_name', 'created_at')
    serializer_class = StartupProfileSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['company_name', 'industry', 'country', 'city', ]
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
            return investor.followed_startups.prefetch_related(
                Prefetch(
                    'projects',
                    queryset=Project.objects.select_related('description')
                )
            )

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

    def get_investor_and_startup(self, startup_pk: int) -> tuple:
        investor = get_object_or_404(InvestorProfile, user=self.request.user)
        startup = get_object_or_404(StartupProfile, pk=startup_pk)
        startup_exists = startup.followers.filter(pk=investor.pk).exists()
        return investor, startup, startup_exists

    @swagger_auto_schema(tags=['Save Follow Startups'])
    @action(detail=True, methods=['post'], url_path='save-favorite', url_name='save-favorite')
    def save_startup(self, request, pk):
        """Add a startup to the user's favourites"""
        investor, startup, startup_exists = self.get_investor_and_startup(pk)
        if startup_exists:
            return Response({'detail': f'{startup} is already followed'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.add(investor)
        return Response({'detail': f'{startup} is saved'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Save Follow Startups'])
    @action(detail=True, methods=['delete'], url_path='delete-favorite', url_name='delete-favorite')
    @method_decorator(ratelimit(key='user_or_ip', rate='30/m'))
    def delete_favorite(self, request, pk):
        """Remove startup from favorites"""
        investor, startup, startup_exists = self.get_investor_and_startup(pk)
        if not startup_exists:
            return Response({'detail': f'{startup} is not in favourites'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.remove(investor)
        return Response({'detail': f'{startup} has been removed'}, status=status.HTTP_200_OK)


class PublicStartupViewSet(ListModelMixin, GenericViewSet):
    """Returns a list of public startups"""
    serializer_class = PublicStartupProfileSerializer
    queryset = StartupProfile.objects.filter(is_public=True)
    pagination_class = PageNumberPagination

    @swagger_auto_schema(tags=['Public Startups'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
