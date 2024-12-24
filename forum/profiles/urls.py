from django.urls import path
from .views import InvestorViewSet, StartupProfileViewSet, SaveStartupViewSet
from rest_framework.routers import DefaultRouter, SimpleRouter

app_name = 'profiles'

router_investor = DefaultRouter()
router_investor.register(r'investor-profile', InvestorViewSet, basename='investor-profile')

router_startup = DefaultRouter()
router_startup.register('startup-profile', StartupProfileViewSet, basename=app_name)

router_startup_save = SimpleRouter()
router_startup_save.register('startups', SaveStartupViewSet, basename='startups')

urlpatterns = router_investor.urls + router_startup.urls + router_startup_save.urls

