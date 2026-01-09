"""URL configuration for devices app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestDeviceViewSet

router = DefaultRouter()
router.register('', TestDeviceViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
]
