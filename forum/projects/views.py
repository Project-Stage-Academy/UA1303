from decimal import Decimal
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from .models import Project
from profiles.models import StartupProfile, InvestorProfile
from .serializers import ProjectSerializer, InvestmentCreateSerializer
from .permissions import IsOwnerOrReadOnly
from .search.services import SearchService


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Project.objects.select_related('description')
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Override the default queryset for GET method (list).
        """
        if self.action in ['list']:
            return Project.objects.select_related('description').filter(is_published=True)
        else:
            return self.queryset

    def perform_create(self, serializer):
        """Automatically assigns project to correct startup based on user's token"""
        startup = StartupProfile.objects.filter(user=self.request.user).first()
        if not startup:
            raise ValidationError({"detail": "You do not have a startup profile. Please create one before creating a project."})
        serializer.save(startup=startup)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('q', '')
        filters = {
            'is_published': True,
            'industry': request.query_params.get('industry'),
            'country': request.query_params.get('country'),
        }
        sort_by = request.query_params.get('sort_by', '-created_at')

        results = SearchService.search_projects(
            query=query,
            filters=filters,
            sort_by=sort_by
        )

        serializer = self.get_serializer(
            [result.to_dict() for result in results],
            many=True
        )
        return Response(serializer.data)


class InvestmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    """
    API View for creating an investment in a project.

    This view allows an investor to create a new investment for a specific project.
    The investor only needs to provide the investment share in the request body.

    Access:
        Only authenticated users can access this endpoint.

    Responses:
        201 Created: If the investment is successfully created.
        400 Bad Request: If the data is invalid or the project is already completed.
    """

    @swagger_auto_schema(
        operation_description="Create an investment for a project",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'share': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal',
                                        description='The share amount of the investment'),
            },
            required=['share']
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Investment successfully created",
                examples={
                    "application/json": {
                        "id": 1,
                        "project": 1,
                        "investor": 1,
                        "share": "50.00"
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: "Bad Request - Invalid data or project completed",
            status.HTTP_403_FORBIDDEN: "Forbidden - User is not an investor",
            status.HTTP_404_NOT_FOUND: "Not Found - Project not found"
        }
    )
    def post(self, request, project_id):
        try:
            investor_profile = InvestorProfile.objects.get(user=request.user)
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Only investors can create investments."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        project = get_object_or_404(Project, id=project_id)
        
        if project.startup.user == request.user:
            return Response(
                {"error": "You cannot invest in your own project."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if project.is_completed:
            return Response(
                {"error": "This project is completely funded."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        share = Decimal(request.data.get('share', '0.00'))
        if project.total_funding + share > project.funding_goal:
            return Response(
                {"error": "Share exceeds the remaining funding goal."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['project'] = project.id
        data['investor'] = investor_profile.id

        serializer = InvestmentCreateSerializer(data=data, context={'project': project})
        if serializer.is_valid():
            try:
                investment = serializer.save(project=project, investor=investor_profile)
                if project.total_funding + investment.share >= project.funding_goal:
                    project.is_completed = True
                    project.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)