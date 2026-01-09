"""Artifact views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Artifact
from .serializers import ArtifactSerializer, ArtifactCreateSerializer, ArtifactSyncSerializer
from apps.users.permissions import IsAdminOrManager


@extend_schema_view(
    list=extend_schema(description='获取制品列表'),
    retrieve=extend_schema(description='获取制品详情'),
    create=extend_schema(description='创建制品'),
    update=extend_schema(description='更新制品'),
    partial_update=extend_schema(description='部分更新制品'),
    destroy=extend_schema(description='删除制品'),
)
class ArtifactViewSet(viewsets.ModelViewSet):
    """ViewSet for artifact management."""
    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer
    filterset_fields = ['artifact_type', 'repository', 'target_device_type']
    search_fields = ['name', 'version', 'description', 'artifact_id']
    ordering_fields = ['created_at', 'name', 'version']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ArtifactCreateSerializer
        elif self.action == 'sync_from_repo':
            return ArtifactSyncSerializer
        return ArtifactSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'sync_from_repo']:
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @extend_schema(
        description='从制品库同步制品',
        request=ArtifactSyncSerializer,
    )
    @action(detail=False, methods=['post'])
    def sync_from_repo(self, request):
        """Sync artifacts from artifact repository."""
        serializer = ArtifactSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .tasks import sync_artifacts_from_repo
        task = sync_artifacts_from_repo.delay(
            repository=serializer.validated_data['repository'],
            group_id=serializer.validated_data.get('group_id'),
            artifact_id=serializer.validated_data.get('artifact_id'),
            version_pattern=serializer.validated_data.get('version_pattern')
        )
        
        return Response({
            'message': '制品同步任务已创建',
            'task_id': task.id
        })
    
    @extend_schema(description='获取特定设备类型的制品')
    @action(detail=False, methods=['get'])
    def by_device_type(self, request):
        """Get artifacts for specific device type."""
        device_type = request.query_params.get('device_type')
        if not device_type:
            return Response({
                'error': '请指定设备类型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        artifacts = self.queryset.filter(target_device_type=device_type)
        serializer = self.get_serializer(artifacts, many=True)
        return Response(serializer.data)
    
    @extend_schema(description='获取最新版本制品')
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest version of artifacts."""
        name = request.query_params.get('name')
        if not name:
            return Response({
                'error': '请指定制品名称'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        artifact = self.queryset.filter(name=name).order_by('-created_at').first()
        if not artifact:
            return Response({
                'error': '未找到指定制品'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(artifact)
        return Response(serializer.data)
