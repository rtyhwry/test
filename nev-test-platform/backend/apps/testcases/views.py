"""Test case views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import TestCase, TestCaseResult
from .serializers import (
    TestCaseSerializer, TestCaseCreateSerializer, TestCaseUpdateSerializer,
    TestCaseBatchCreateSerializer, TestCaseResultSerializer
)
from apps.users.permissions import IsEngineerOrAbove


@extend_schema_view(
    list=extend_schema(description='获取测试用例列表'),
    retrieve=extend_schema(description='获取测试用例详情'),
    create=extend_schema(description='创建测试用例'),
    update=extend_schema(description='更新测试用例'),
    partial_update=extend_schema(description='部分更新测试用例'),
    destroy=extend_schema(description='删除测试用例'),
)
class TestCaseViewSet(viewsets.ModelViewSet):
    """ViewSet for test case management."""
    queryset = TestCase.objects.select_related('task')
    serializer_class = TestCaseSerializer
    filterset_fields = ['task', 'status', 'priority', 'module']
    search_fields = ['name', 'case_code', 'description', 'alm_case_id']
    ordering_fields = ['created_at', 'execution_order', 'priority']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TestCaseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TestCaseUpdateSerializer
        elif self.action == 'batch_create':
            return TestCaseBatchCreateSerializer
        return TestCaseSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'batch_create']:
            return [IsEngineerOrAbove()]
        return [IsAuthenticated()]
    
    @extend_schema(
        description='批量创建测试用例',
        request=TestCaseBatchCreateSerializer,
        responses={201: TestCaseSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """Batch create test cases."""
        serializer = TestCaseBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task_id = serializer.validated_data['task_id']
        cases_data = serializer.validated_data['cases']
        
        created_cases = []
        for case_data in cases_data:
            case_data['task_id'] = task_id
            case = TestCase.objects.create(**case_data)
            created_cases.append(case)
        
        return Response(
            TestCaseSerializer(created_cases, many=True).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(description='获取用例执行历史')
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get test case execution results."""
        test_case = self.get_object()
        results = test_case.results.all()[:20]
        serializer = TestCaseResultSerializer(results, many=True)
        return Response(serializer.data)


class TestCaseResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for test case results."""
    queryset = TestCaseResult.objects.select_related('execution', 'test_case')
    serializer_class = TestCaseResultSerializer
    filterset_fields = ['execution', 'test_case', 'status']
    search_fields = ['test_case__name', 'test_case__case_code']
    ordering_fields = ['created_at', 'start_time', 'status']
    permission_classes = [IsAuthenticated]
