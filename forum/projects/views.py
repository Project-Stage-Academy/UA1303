from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Project
from profiles.models import StartupProfile
from .serializers import ProjectSerializer
from .permissions import IsOwnerOrReadOnly


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Project.objects.select_related('description')
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        """Automatically assigns project to correct startup based on user's token"""
        startup = StartupProfile.objects.filter(user=self.request.user).first()
        if not startup:
            raise ValidationError({"detail": "You do not have a startup profile. Please create one before creating a project."})
        serializer.save(startup=startup)
