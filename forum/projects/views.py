from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


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

    def post(self, request, project_id):
        """
        Handle investment creation for a given project.
        """
        project = get_object_or_404(Project, id=project_id)
        if project.is_completed:
            return Response({"error: This project is completely funded."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InvestmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(project=project, investor=request.user.investorprofile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
