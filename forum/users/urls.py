from django.urls import path
from .views import RegisterUserView

app_name = 'users'

urlpatterns = [
    path('user-register/', RegisterUserView.as_view(), name='user-register'),
]
