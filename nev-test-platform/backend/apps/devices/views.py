"""Test device views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import TestDevice, DeviceUpgradeHistory
from .serializers import (
    TestDeviceSerializer, TestDeviceCreateSerializer,
    TestDeviceUpdateSerializer, DeviceUpgradeRequestSerializer,
    DeviceUpgradeHistorySerializer
)
from apps.users.permissions import IsAdminOrManager, IsEngineerOrAbove


@extend_schema_view(
    list=extend_schema(description='获取设备列表'),
    retrieve=extend_schema(description='获取设备详情'),
    create=extend_schema(description='注册设备'),
    update=extend_schema(description='更新设备'),
    partial_update=extend_schema(description='部分更新设备'),
    destroy=extend_schema(description='删除设备'),
)
class TestDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for test device management."""
    queryset = TestDevice.objects.all()
    serializer_class = TestDeviceSerializer
    filterset_fields = ['device_type', 'status', 'environment']
    search_fields = ['name', 'serial_number', 'manufacturer', 'model', 'description']
    ordering_fields = ['created_at', 'name', 'device_type', 'status']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TestDeviceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TestDeviceUpdateSerializer
        elif self.action == 'upgrade':
            return DeviceUpgradeRequestSerializer
        return TestDeviceSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create', 'destroy']:
            return [IsAdminOrManager()]
        elif self.action in ['update', 'partial_update', 'upgrade']:
            return [IsEngineerOrAbove()]
        return [IsAuthenticated()]
    
    @extend_schema(
        description='升级设备',
        request=DeviceUpgradeRequestSerializer,
        responses={200: DeviceUpgradeHistorySerializer}
    )
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        """Upgrade device firmware/software."""
        device = self.get_object()
        serializer = DeviceUpgradeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.artifacts.models import Artifact
        try:
            artifact = Artifact.objects.get(id=serializer.validated_data['artifact_id'])
        except Artifact.DoesNotExist:
            return Response({
                'error': '指定的制品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already at target version
        if not serializer.validated_data.get('force', False):
            if device.software_version == artifact.version:
                return Response({
                    'message': '设备已是目标版本，无需升级'
                })
        
        # Create upgrade history record
        upgrade = DeviceUpgradeHistory.objects.create(
            device=device,
            artifact=artifact,
            from_version=device.software_version,
            to_version=artifact.version,
            operated_by=request.user
        )
        
        # Trigger async upgrade task
        from .tasks import upgrade_device
        task = upgrade_device.delay(device.id, artifact.id, upgrade.id)
        
        return Response({
            'message': '设备升级任务已创建',
            'upgrade_id': upgrade.id,
            'task_id': task.id
        })
    
    @extend_schema(description='获取设备升级历史')
    @action(detail=True, methods=['get'])
    def upgrade_history(self, request, pk=None):
        """Get device upgrade history."""
        device = self.get_object()
        history = device.upgrade_history.all()[:20]
        serializer = DeviceUpgradeHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @extend_schema(description='获取可用设备列表')
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get list of available devices."""
        devices = self.queryset.filter(status=TestDevice.Status.AVAILABLE)
        serializer = self.get_serializer(devices, many=True)
        return Response(serializer.data)
