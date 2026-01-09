"""URL configuration for hosts app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestHostViewSet

router = DefaultRouter()
router.register('', TestHostViewSet, basename='host')

urlpatterns = [
    path('', include(router.urls)),
]
