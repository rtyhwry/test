"""
URL configuration for NEV Test Platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/users/', include('apps.users.urls_users')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/hosts/', include('apps.hosts.urls')),
    path('api/v1/devices/', include('apps.devices.urls')),
    path('api/v1/environments/', include('apps.environments.urls')),
    path('api/v1/artifacts/', include('apps.artifacts.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/testcases/', include('apps.testcases.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
