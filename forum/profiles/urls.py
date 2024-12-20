from rest_framework.routers import DefaultRouter
from .views import StartupProfileViewSet

app_name = 'profiles'

router_startup = DefaultRouter()
router_startup.register('startup-profile', StartupProfileViewSet, basename=app_name)

# Modify Investor router so startups and investors will have different prefixes
# router_investor = DefaultRouter()
# router_investor.register('investor-profile', #InvestorProfileViewSetHere, basename=app_name)

# Add investor router to url patterns
urlpatterns = router_startup.urls
