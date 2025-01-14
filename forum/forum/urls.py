"""forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.urls import auth_urlpatterns


APP_URLS = [
    ('communications', 'communications.urls'),
    ('dashboard', 'dashboard.urls'),
    ('notifications', 'notifications.urls'),
]

APP_ROUTER_URLS = [
    ('profiles', 'profiles.urls'),
    ('projects', 'projects.urls'),
]

api_urlpatterns = [
    path('api/v1/auth/', include((auth_urlpatterns, 'auth'), namespace='auth')),

    *[path(f'api/v1/{app}/', include(urls_file, namespace=app)) for app, urls_file in APP_URLS],
]

api_router_urlpatterns = [
    *[path(f'api/v1/{app}/', include(urls_file, namespace=app)) for app, urls_file in APP_ROUTER_URLS],
]

api_urlpatterns = format_suffix_patterns(api_urlpatterns) + api_router_urlpatterns

schema_view = get_schema_view(
   openapi.Info(
      title="Forum API",
      default_version='v1',
      description="API documentation for forum app",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="some@email.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf'))
] + api_urlpatterns