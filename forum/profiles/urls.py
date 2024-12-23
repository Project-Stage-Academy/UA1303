from django.urls import path
from .views import InvestorViewSet, StartupProfileViewSet, SaveStartupView
from rest_framework.routers import DefaultRouter

app_name = 'profiles'

router_investor = DefaultRouter()
router_investor.register(r'investor-profile', InvestorViewSet, basename='investor-profile')

router_startup = DefaultRouter()
router_startup.register('startup-profile', StartupProfileViewSet, basename=app_name)

urlpatterns = router_investor.urls
urlpatterns = [
    path('api/startups/<int:startup_id>/save', SaveStartupView.as_view(), name='save-startup'),
              ] + urlpatterns + router_startup.urls

