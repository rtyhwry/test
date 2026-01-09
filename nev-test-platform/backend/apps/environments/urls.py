"""URL configuration for environments app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestEnvironmentViewSet

router = DefaultRouter()
router.register('', TestEnvironmentViewSet, basename='environment')

urlpatterns = [
    path('', include(router.urls)),
]
