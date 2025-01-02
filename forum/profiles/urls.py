# from rest_framework.routers import DefaultRouter, SimpleRouter
#
# from .views import InvestorViewSet, StartupProfileViewSet, SaveStartupViewSet
#
# app_name = 'profiles'
#
# # Define a single DefaultRouter for all default routes
# router = DefaultRouter()
#
# # Register Investor and Startup routes
# router.register(r'investor-profile', InvestorViewSet, basename='investor-profile')
# router.register(r'startup-profile', StartupProfileViewSet, basename='startup-profile')
#
# # Define a separate SimpleRouter for "SaveStartupViewSet" if needed
# simple_router = SimpleRouter()
# simple_router.register(r'startups', SaveStartupViewSet, basename='startups')
#
# # Combine all URLs
# urlpatterns = router.urls + simple_router.urls

from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import InvestorViewSet, StartupProfileViewSet, SaveStartupViewSet

app_name = 'profiles'

router_investor = DefaultRouter()
router_investor.register(r'investor-profile', InvestorViewSet, basename='investor-profile')

router_startup = DefaultRouter()
router_startup.register(r'startup-profile', StartupProfileViewSet, basename=app_name)

router_startup_save = SimpleRouter()
router_startup_save.register('startups', SaveStartupViewSet, basename='startups')

urlpatterns = router_investor.urls + router_startup.urls + router_startup_save.urls