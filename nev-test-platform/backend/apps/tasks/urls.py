"""URL configuration for tasks app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestTaskViewSet, TaskExecutionViewSet

router = DefaultRouter()
router.register('', TestTaskViewSet, basename='task')
router.register('executions', TaskExecutionViewSet, basename='execution')

urlpatterns = [
    path('', include(router.urls)),
]
