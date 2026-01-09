"""URL configuration for reports app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestReportViewSet

router = DefaultRouter()
router.register('', TestReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
