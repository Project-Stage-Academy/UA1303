from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
import logging

logger = logging.getLogger(__name__)


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        startup = self.request.user.startup_profile
        serializer.save(startup=startup)

    # def update(self, request, *args, **kwargs):
    #     project_instance = self.get_object()
    #
