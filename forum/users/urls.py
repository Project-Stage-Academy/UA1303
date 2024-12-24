from django.urls import path
from .views import password_reset_with_captcha
from .views import LogoutView
from .views import RegisterUserView

app_name = 'users'

auth_urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-register/', RegisterUserView.as_view(), name='user-register'),
]

urlpatterns = [
    path('password/reset/', password_reset_with_captcha, name='password_reset_captcha'),
]