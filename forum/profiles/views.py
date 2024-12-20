from rest_framework.viewsets import ModelViewSet
from .models import InvestorProfile
from .serializers import InvestorProfileSerializer
from rest_framework.permissions import IsAuthenticated


class InvestorViewSet(ModelViewSet):
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [
        IsAuthenticated
    ] 

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestorProfile.objects.all()
        return InvestorProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
