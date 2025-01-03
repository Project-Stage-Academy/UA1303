from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import InvestorViewSet, StartupProfileViewSet, SaveStartupViewSet, PublicStartupViewSet, PublicStartupFilterViewSet

app_name = 'profiles'

router = DefaultRouter()
router.register(r'investor-profile', InvestorViewSet, basename='investor-profile')
router.register('startup-profile', StartupProfileViewSet, basename='startup-profile')
router.register('startups', SaveStartupViewSet, basename='startups')
router.register('public-startups', PublicStartupViewSet, basename='public-startups')
router.register('public-startups-filter', PublicStartupFilterViewSet, basename='public-startup-filter')

urlpatterns = router.urls
