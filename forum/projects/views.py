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
from profiles.models import StartupProfile
from .serializers import ProjectSerializer, InvestmentCreateSerializer
from .permissions import IsOwnerOrReadOnly


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
            status.HTTP_400_BAD_REQUEST: "Bad Request - Invalid data or project completed"
        }
    )
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if project.is_completed:
            return Response({"error: This project is completely funded."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['project'] = project.id
        data['investor'] = request.user.investor_profile.id

        serializer = InvestmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(project=project, investor=request.user.investor_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
