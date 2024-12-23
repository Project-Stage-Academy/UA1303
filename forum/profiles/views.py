from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import InvestorProfile, StartupProfile
from .serializers import InvestorProfileSerializer, StartupProfileSerializer
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


class StartupProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer

    def perform_create(self, serializer):
        """Automatically assigns startup profile to the right user based on user's token"""
        serializer.save(user=self.request.user)


class SaveStartupView(APIView):
    """Adds startup to user's favourites"""
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        investor = get_object_or_404(InvestorProfile, user=request.user)
        startup = get_object_or_404(StartupProfile, pk=startup_id)
        if startup.followers.filter(pk=investor.pk).exists():
            return Response({'detail': 'Startup is already followed'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.add(investor)
        return Response({'detail': 'Startup is saved'}, status=status.HTTP_200_OK)
