from django.urls import path
from .views import password_reset_with_captcha


app_name = 'users'

urlpatterns = [
    path('password/reset/', password_reset_with_captcha, name='password_reset_captcha'),
]
