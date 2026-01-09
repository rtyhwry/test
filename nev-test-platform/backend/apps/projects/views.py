"""Project views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Project
from .serializers import ProjectSerializer, ProjectCreateSerializer, ProjectUpdateSerializer
from apps.users.permissions import IsAdminOrManager


@extend_schema_view(
    list=extend_schema(description='获取项目列表'),
    retrieve=extend_schema(description='获取项目详情'),
    create=extend_schema(description='创建项目'),
    update=extend_schema(description='更新项目'),
    partial_update=extend_schema(description='部分更新项目'),
    destroy=extend_schema(description='删除项目'),
)
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for project management."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_fields = ['owner']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['created_at', 'name', 'code']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ProjectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        return ProjectSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get project statistics."""
        project = self.get_object()
        
        # Get statistics
        stats = {
            'environment_count': project.environments.count(),
            'task_count': project.tasks.count(),
            'total_executions': 0,
            'passed_executions': 0,
            'failed_executions': 0,
        }
        
        # Calculate execution statistics
        for task in project.tasks.all():
            executions = task.executions.all()
            stats['total_executions'] += executions.count()
            stats['passed_executions'] += executions.filter(status='completed').count()
            stats['failed_executions'] += executions.filter(status='failed').count()
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def environments(self, request, pk=None):
        """Get environments for project."""
        project = self.get_object()
        from apps.environments.serializers import TestEnvironmentSerializer
        serializer = TestEnvironmentSerializer(project.environments.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get tasks for project."""
        project = self.get_object()
        from apps.tasks.serializers import TestTaskSerializer
        serializer = TestTaskSerializer(project.tasks.all(), many=True)
        return Response(serializer.data)
