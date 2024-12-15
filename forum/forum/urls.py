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
from django.http import HttpResponse, JsonResponse
from django.urls import path, include, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def test(request):
    return HttpResponse('Testing...')


@api_view(['GET'])
def api_test(request,format=None):
    return Response({"testing":"OK"})

APP_URLS = [
    ('users', 'users.urls'),
    ('profiles', 'profiles.urls'),
    ('projects', 'projects.urls'),
    ('communications', 'communications.urls'),
    ('dashboard', 'dashboard.urls'),
    ('notifications', 'notifications.urls'),
]

api_urlpatterns = [
    path('api/test/', api_test, name='api_test'),

    *[path(f'api/v1/{app}/', include(urls_file, namespace=app)) for app, urls_file in APP_URLS],
]

api_urlpatterns=format_suffix_patterns(api_urlpatterns)

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
    path('',test,name='test'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
] + api_urlpatterns