from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer

app_name = 'users'

urlpatterns = [
    path('sign-in/', TokenObtainPairView.as_view(), name='sign_in'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
