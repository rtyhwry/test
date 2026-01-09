"""URL configuration for testcases app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestCaseViewSet, TestCaseResultViewSet

router = DefaultRouter()
router.register('', TestCaseViewSet, basename='testcase')
router.register('results', TestCaseResultViewSet, basename='testcase-result')

urlpatterns = [
    path('', include(router.urls)),
]
