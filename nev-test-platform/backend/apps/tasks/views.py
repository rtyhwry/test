"""Test task views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import TestTask, TaskExecution, ExecutionLog
from .serializers import (
    TestTaskSerializer, TestTaskCreateSerializer, TestTaskUpdateSerializer,
    ExecuteTaskSerializer, TaskExecutionSerializer, ExecutionLogSerializer
)
from apps.users.permissions import IsAdminOrManager, IsEngineerOrAbove


@extend_schema_view(
    list=extend_schema(description='获取任务列表'),
    retrieve=extend_schema(description='获取任务详情'),
    create=extend_schema(description='创建任务'),
    update=extend_schema(description='更新任务'),
    partial_update=extend_schema(description='部分更新任务'),
    destroy=extend_schema(description='删除任务'),
)
class TestTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for test task management."""
    queryset = TestTask.objects.select_related('project', 'environment', 'artifact', 'created_by')
    serializer_class = TestTaskSerializer
    filterset_fields = ['project', 'environment', 'status', 'schedule_type', 'is_enabled']
    search_fields = ['name', 'description', 'alm_task_id']
    ordering_fields = ['created_at', 'name', 'priority', 'status']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TestTaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TestTaskUpdateSerializer
        elif self.action == 'execute':
            return ExecuteTaskSerializer
        return TestTaskSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['destroy']:
            return [IsAdminOrManager()]
        elif self.action in ['create', 'update', 'partial_update', 'execute', 'cancel']:
            return [IsEngineerOrAbove()]
        return [IsAuthenticated()]
    
    @extend_schema(
        description='执行任务',
        request=ExecuteTaskSerializer,
        responses={200: TaskExecutionSerializer}
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a test task."""
        task = self.get_object()
        
        # Check if task is enabled
        if not task.is_enabled:
            return Response({
                'error': '任务已禁用，无法执行'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if task is already running
        if task.status == TestTask.Status.RUNNING:
            return Response({
                'error': '任务正在执行中'
            }, status=status.HTTP_409_CONFLICT)
        
        serializer = ExecuteTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Determine environment
        environment_id = serializer.validated_data.get('environment_id') or (task.environment.id if task.environment else None)
        if not environment_id:
            return Response({
                'error': '请指定执行环境'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.environments.models import TestEnvironment
        try:
            environment = TestEnvironment.objects.get(id=environment_id)
        except TestEnvironment.DoesNotExist:
            return Response({
                'error': '指定的环境不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check environment availability
        if not environment.is_available:
            return Response({
                'error': f'环境 {environment.name} 当前不可用'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create execution record
        execution = TaskExecution.objects.create(
            task=task,
            environment=environment,
            triggered_by=TaskExecution.TriggerType.MANUAL,
            triggered_user=request.user,
            artifact_version=task.artifact.version if task.artifact else '',
        )
        
        # Update task status
        task.status = TestTask.Status.QUEUED
        task.save()
        
        # Lock environment
        environment.status = TestEnvironment.Status.IN_USE
        environment.locked_by = request.user
        environment.locked_at = timezone.now()
        environment.lock_reason = f'执行任务: {task.name}'
        environment.save()
        
        # Trigger async execution
        from .tasks import execute_test_task
        celery_task = execute_test_task.delay(
            execution.id,
            force_upgrade=serializer.validated_data.get('force_upgrade', False)
        )
        
        execution.celery_task_id = celery_task.id
        execution.save()
        
        return Response({
            'message': '任务已开始执行',
            'execution': TaskExecutionSerializer(execution).data
        })
    
    @extend_schema(description='取消任务执行')
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a running task."""
        task = self.get_object()
        
        if task.status not in [TestTask.Status.QUEUED, TestTask.Status.RUNNING]:
            return Response({
                'error': '只能取消排队中或执行中的任务'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get latest execution
        execution = task.executions.filter(
            status__in=[TaskExecution.Status.PENDING, TaskExecution.Status.RUNNING]
        ).first()
        
        if execution and execution.celery_task_id:
            # Revoke Celery task
            from config.celery import app
            app.control.revoke(execution.celery_task_id, terminate=True)
            
            execution.status = TaskExecution.Status.CANCELLED
            execution.end_time = timezone.now()
            execution.save()
        
        task.status = TestTask.Status.CANCELLED
        task.save()
        
        # Release environment
        if execution and execution.environment:
            from apps.environments.models import TestEnvironment
            execution.environment.status = TestEnvironment.Status.AVAILABLE
            execution.environment.locked_by = None
            execution.environment.locked_at = None
            execution.environment.lock_reason = ''
            execution.environment.save()
        
        return Response({'message': '任务已取消'})
    
    @extend_schema(description='获取任务执行历史')
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get task execution history."""
        task = self.get_object()
        executions = task.executions.all()[:50]
        serializer = TaskExecutionSerializer(executions, many=True)
        return Response(serializer.data)
    
    @extend_schema(description='启用任务')
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a task."""
        task = self.get_object()
        task.is_enabled = True
        task.status = TestTask.Status.PENDING
        task.save()
        return Response({'message': '任务已启用'})
    
    @extend_schema(description='禁用任务')
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a task."""
        task = self.get_object()
        task.is_enabled = False
        task.status = TestTask.Status.PAUSED
        task.save()
        return Response({'message': '任务已禁用'})


class TaskExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for task execution records."""
    queryset = TaskExecution.objects.select_related('task', 'environment', 'triggered_user')
    serializer_class = TaskExecutionSerializer
    filterset_fields = ['task', 'environment', 'status', 'triggered_by']
    search_fields = ['task__name']
    ordering_fields = ['created_at', 'start_time', 'status']
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取执行日志')
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get execution logs."""
        execution = self.get_object()
        logs = execution.logs.all()
        serializer = ExecutionLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @extend_schema(description='获取执行统计')
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get execution statistics."""
        from django.db.models import Count, Avg
        from datetime import timedelta
        
        # Get statistics for last 30 days
        start_date = timezone.now() - timedelta(days=30)
        
        stats = TaskExecution.objects.filter(
            created_at__gte=start_date
        ).aggregate(
            total=Count('id'),
            completed=Count('id', filter=models.Q(status='completed')),
            failed=Count('id', filter=models.Q(status='failed')),
            avg_duration=Avg('duration_seconds')
        )
        
        # Calculate pass rate
        total = stats['total'] or 0
        completed = stats['completed'] or 0
        success_rate = round(completed / total * 100, 2) if total > 0 else 0
        
        return Response({
            'total_executions': total,
            'completed': completed,
            'failed': stats['failed'] or 0,
            'success_rate': success_rate,
            'avg_duration_seconds': round(stats['avg_duration'] or 0, 2)
        })
