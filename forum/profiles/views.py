from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import InvestorProfile
from .serializers import InvestorProfileSerializer
from .permissions import IsOwnerOrReadOnly


class InvestorViewSet(ModelViewSet):

    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]

    def get_queryset(self):
        return InvestorProfile.objects.filter(user=self.request.user).select_related(
            "user"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)