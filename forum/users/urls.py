from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import password_reset_with_captcha
from .views import LogoutView
from .views import RegisterUserView, CustomUserViewSet, ChangeRoleView, GithubAccessTokenView

app_name = 'users'

auth_urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-register/', RegisterUserView.as_view(), name='user-register'),
    path('me/', CustomUserViewSet.as_view({'get': 'retrieve'}), name='me'),
    path('password/reset/', password_reset_with_captcha, name='password_reset_captcha'),
    path('change-role/', ChangeRoleView.as_view(), name='change_role'),
    path('github-token/', GithubAccessTokenView.as_view(), name='github-token')
]
