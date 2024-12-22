from django.urls import path
from .views import LogoutView


app_name = 'users'

auth_urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
]

urlpatterns = [
    
]