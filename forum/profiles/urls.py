from django.urls import path
from .views import InvestorViewSet
from rest_framework.routers import DefaultRouter

app_name = 'profiles'

router = DefaultRouter()
router.register(r'investor-profile', InvestorViewSet, basename='investor-profile')

urlpatterns = router.urls