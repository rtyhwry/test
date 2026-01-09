"""Test environment views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import TestEnvironment
from .serializers import (
    TestEnvironmentSerializer, TestEnvironmentCreateSerializer,
    TestEnvironmentUpdateSerializer, EnvironmentLockSerializer,
    EnvironmentUnlockSerializer
)
from apps.users.permissions import IsAdminOrManager, IsEngineerOrAbove


@extend_schema_view(
    list=extend_schema(description='获取环境列表'),
    retrieve=extend_schema(description='获取环境详情'),
    create=extend_schema(description='创建环境'),
    update=extend_schema(description='更新环境'),
    partial_update=extend_schema(description='部分更新环境'),
    destroy=extend_schema(description='删除环境'),
)
class TestEnvironmentViewSet(viewsets.ModelViewSet):
    """ViewSet for test environment management."""
    queryset = TestEnvironment.objects.select_related('project', 'host', 'locked_by').prefetch_related('devices')
    serializer_class = TestEnvironmentSerializer
    filterset_fields = ['project', 'host', 'status']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['created_at', 'name', 'status']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TestEnvironmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TestEnvironmentUpdateSerializer
        elif self.action == 'lock':
            return EnvironmentLockSerializer
        elif self.action == 'unlock':
            return EnvironmentUnlockSerializer
        return TestEnvironmentSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create', 'destroy']:
            return [IsAdminOrManager()]
        elif self.action in ['update', 'partial_update', 'lock', 'unlock']:
            return [IsEngineerOrAbove()]
        return [IsAuthenticated()]
    
    @extend_schema(
        description='锁定环境',
        request=EnvironmentLockSerializer,
        responses={200: TestEnvironmentSerializer}
    )
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock environment for exclusive use."""
        environment = self.get_object()
        
        # Check if already locked
        if environment.is_locked:
            if environment.locked_by == request.user:
                return Response({
                    'message': '您已锁定此环境'
                })
            return Response({
                'error': f'环境已被 {environment.locked_by.username} 锁定'
            }, status=status.HTTP_409_CONFLICT)
        
        # Check if environment is available
        if environment.status not in [TestEnvironment.Status.AVAILABLE]:
            return Response({
                'error': f'环境当前状态为 {environment.get_status_display()}，无法锁定'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EnvironmentLockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Lock the environment
        duration_hours = serializer.validated_data.get('duration_hours', environment.max_lock_hours)
        
        environment.status = TestEnvironment.Status.LOCKED
        environment.locked_by = request.user
        environment.locked_at = timezone.now()
        environment.lock_reason = serializer.validated_data.get('reason', '')
        environment.lock_expires_at = timezone.now() + timedelta(hours=duration_hours)
        environment.save()
        
        return Response({
            'message': '环境锁定成功',
            'data': TestEnvironmentSerializer(environment).data
        })
    
    @extend_schema(
        description='解锁环境',
        request=EnvironmentUnlockSerializer,
        responses={200: TestEnvironmentSerializer}
    )
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock environment."""
        environment = self.get_object()
        
        # Check if locked
        if not environment.is_locked:
            return Response({
                'message': '环境未被锁定'
            })
        
        serializer = EnvironmentUnlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check permission
        force = serializer.validated_data.get('force', False)
        if environment.locked_by != request.user:
            if not (force and request.user.is_manager):
                return Response({
                    'error': '只有锁定者或管理员才能解锁此环境'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Unlock the environment
        environment.status = TestEnvironment.Status.AVAILABLE
        environment.locked_by = None
        environment.locked_at = None
        environment.lock_reason = ''
        environment.lock_expires_at = None
        environment.save()
        
        return Response({
            'message': '环境解锁成功',
            'data': TestEnvironmentSerializer(environment).data
        })
    
    @extend_schema(description='获取可用环境列表')
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get list of available environments."""
        project_id = request.query_params.get('project')
        
        queryset = self.queryset.filter(status=TestEnvironment.Status.AVAILABLE)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(description='获取我锁定的环境')
    @action(detail=False, methods=['get'])
    def my_locked(self, request):
        """Get environments locked by current user."""
        environments = self.queryset.filter(locked_by=request.user)
        serializer = self.get_serializer(environments, many=True)
        return Response(serializer.data)
