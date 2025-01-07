from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, InvestmentCreateView

app_name = 'projects'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename=app_name)


urlpatterns = [
    path(
        "api/v1/projects/<int:project_id>/investment/",
        InvestmentCreateView.as_view(),
        name="project-investment"
    ),
] + router.urls
