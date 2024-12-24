from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import InvestorProfile, StartupProfile
from .serializers import InvestorProfileSerializer, StartupProfileSerializer
from .permissions import IsOwnerOrReadOnly


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


class SaveStartupViewSet(GenericViewSet):
    """Adds startup to user's favourites"""
    permission_classes = [IsAuthenticated]
    serializer_class = Serializer
    queryset = StartupProfile.objects.all()

    @action(detail=True, methods=['post'], url_path='save', url_name='save')
    def post(self, request, pk):
        investor = get_object_or_404(InvestorProfile, user=request.user)
        startup = get_object_or_404(StartupProfile, pk=pk)
        if startup.followers.filter(pk=investor.pk).exists():
            return Response({'detail': 'Startup is already followed'}, status=status.HTTP_400_BAD_REQUEST)
        startup.followers.add(investor)
        return Response({'detail': 'Startup is saved'}, status=status.HTTP_200_OK)
