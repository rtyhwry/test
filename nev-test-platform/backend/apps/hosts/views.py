"""Test host views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import TestHost
from .serializers import (
    TestHostSerializer, TestHostCreateSerializer,
    TestHostUpdateSerializer, HostStatusSerializer
)
from apps.users.permissions import IsAdminOrManager
from .services import HostConnectionService


@extend_schema_view(
    list=extend_schema(description='获取主机列表'),
    retrieve=extend_schema(description='获取主机详情'),
    create=extend_schema(description='注册主机'),
    update=extend_schema(description='更新主机'),
    partial_update=extend_schema(description='部分更新主机'),
    destroy=extend_schema(description='删除主机'),
)
class TestHostViewSet(viewsets.ModelViewSet):
    """ViewSet for test host management."""
    queryset = TestHost.objects.all()
    serializer_class = TestHostSerializer
    filterset_fields = ['status', 'os_type']
    search_fields = ['name', 'hostname', 'ip_address', 'description']
    ordering_fields = ['created_at', 'name', 'status']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TestHostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TestHostUpdateSerializer
        return TestHostSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @extend_schema(
        description='测试主机连接',
        responses={200: HostStatusSerializer}
    )
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SSH connection to host."""
        host = self.get_object()
        service = HostConnectionService(host)
        
        try:
            result = service.test_connection()
            if result['success']:
                host.status = TestHost.Status.ONLINE
                host.last_heartbeat = timezone.now()
                host.save()
                return Response({
                    'success': True,
                    'message': '连接成功',
                    'data': result.get('data', {})
                })
            else:
                host.status = TestHost.Status.OFFLINE
                host.save()
                return Response({
                    'success': False,
                    'message': result.get('error', '连接失败')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            host.status = TestHost.Status.OFFLINE
            host.save()
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        description='获取主机实时状态',
        responses={200: HostStatusSerializer}
    )
    @action(detail=True, methods=['get'])
    def status_info(self, request, pk=None):
        """Get real-time host status."""
        host = self.get_object()
        service = HostConnectionService(host)
        
        try:
            status_info = service.get_system_info()
            return Response(status_info)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(description='批量检查主机状态')
    @action(detail=False, methods=['post'])
    def check_all(self, request):
        """Check status of all hosts."""
        from .tasks import check_all_hosts_status
        task = check_all_hosts_status.delay()
        return Response({
            'message': '已开始检查所有主机状态',
            'task_id': task.id
        })
