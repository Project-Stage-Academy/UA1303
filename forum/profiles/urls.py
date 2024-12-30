from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import InvestorViewSet, StartupProfileViewSet, SaveStartupViewSet, PublicStartupViewSet

app_name = 'profiles'

router_investor = DefaultRouter()
router_investor.register(r'investor-profile', InvestorViewSet, basename='investor-profile')

router_startup = DefaultRouter()
router_startup.register('startup-profile', StartupProfileViewSet, basename=app_name)

router_startup_save = SimpleRouter()
router_startup_save.register('startups', SaveStartupViewSet, basename='startups')

router_public_startup = DefaultRouter()
router_public_startup.register('public-startups', PublicStartupViewSet, basename='public-startups')

urlpatterns = router_investor.urls + router_startup.urls + router_startup_save.urls + router_public_startup.urls
