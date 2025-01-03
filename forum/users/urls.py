from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer
from .views import password_reset_with_captcha
from .views import LogoutView
from .views import RegisterUserView, CustomUserViewSet

app_name = 'users'

auth_urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-register/', RegisterUserView.as_view(), name='user-register'),
    path('me/', CustomUserViewSet.as_view({'get': 'retrieve'}), name='me'),
    path('password/reset/', password_reset_with_captcha, name='password_reset_captcha'),
]

# urlpatterns = [
#
#     path('password/reset/', password_reset_with_captcha, name='password_reset_captcha'),
# ]
