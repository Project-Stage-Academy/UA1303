from django.urls import path
from .views import password_reset_with_captcha
from .views import LogoutView


app_name = 'users'

auth_urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
]

urlpatterns = [
    path('password/reset/', password_reset_with_captcha, name='password_reset_captcha'),
]