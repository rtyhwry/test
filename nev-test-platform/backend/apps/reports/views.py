"""Test report views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
import os

from .models import TestReport
from .serializers import TestReportSerializer, ReportGenerateSerializer, ReportStatisticsSerializer


@extend_schema_view(
    list=extend_schema(description='获取报告列表'),
    retrieve=extend_schema(description='获取报告详情'),
)
class TestReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for test reports."""
    queryset = TestReport.objects.select_related('execution', 'execution__task')
    serializer_class = TestReportSerializer
    filterset_fields = ['execution__task', 'alm_synced']
    search_fields = ['title', 'summary', 'execution__task__name']
    ordering_fields = ['created_at', 'pass_rate']
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='下载HTML报告')
    @action(detail=True, methods=['get'])
    def download_html(self, request, pk=None):
        """Download HTML report."""
        report = self.get_object()
        if not report.html_report_path or not os.path.exists(report.html_report_path):
            return Response({'error': 'HTML报告不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            open(report.html_report_path, 'rb'),
            as_attachment=True,
            filename=f'report_{report.id}.html'
        )
    
    @extend_schema(description='下载PDF报告')
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download PDF report."""
        report = self.get_object()
        if not report.pdf_report_path or not os.path.exists(report.pdf_report_path):
            return Response({'error': 'PDF报告不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            open(report.pdf_report_path, 'rb'),
            as_attachment=True,
            filename=f'report_{report.id}.pdf'
        )
    
    @extend_schema(description='下载Excel报告')
    @action(detail=True, methods=['get'])
    def download_excel(self, request, pk=None):
        """Download Excel report."""
        report = self.get_object()
        if not report.excel_report_path or not os.path.exists(report.excel_report_path):
            return Response({'error': 'Excel报告不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            open(report.excel_report_path, 'rb'),
            as_attachment=True,
            filename=f'report_{report.id}.xlsx'
        )
    
    @extend_schema(
        description='重新生成报告',
        request=ReportGenerateSerializer
    )
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate report."""
        report = self.get_object()
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .tasks import generate_report
        task = generate_report.delay(
            report.execution.id,
            formats=serializer.validated_data.get('formats', ['html']),
            include_logs=serializer.validated_data.get('include_logs', True),
            include_screenshots=serializer.validated_data.get('include_screenshots', True)
        )
        
        return Response({
            'message': '报告重新生成任务已创建',
            'task_id': task.id
        })
    
    @extend_schema(
        description='获取报告统计',
        responses={200: ReportStatisticsSerializer}
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get report statistics."""
        from django.db.models import Sum, Avg, Count
        from datetime import timedelta
        from django.utils import timezone
        
        # Get time range
        days = int(request.query_params.get('days', 30))
        project_id = request.query_params.get('project')
        
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.queryset.filter(created_at__gte=start_date)
        if project_id:
            queryset = queryset.filter(execution__task__project_id=project_id)
        
        stats = queryset.aggregate(
            total_executions=Count('id'),
            total_cases_executed=Sum('total_cases'),
            total_passed=Sum('passed_cases'),
            total_failed=Sum('failed_cases'),
            average_pass_rate=Avg('pass_rate'),
            average_duration_seconds=Avg('total_duration_seconds')
        )
        
        # Handle None values
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
        
        return Response(stats)
    
    @extend_schema(description='同步报告到ALM')
    @action(detail=True, methods=['post'])
    def sync_to_alm(self, request, pk=None):
        """Sync report results to ALM."""
        report = self.get_object()
        
        from .tasks import sync_report_to_alm
        task = sync_report_to_alm.delay(report.id)
        
        return Response({
            'message': 'ALM同步任务已创建',
            'task_id': task.id
        })
