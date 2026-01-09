"""Integration views for API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .services import GitLabService, ALMService, ArtifactRepoService
from apps.users.permissions import IsAdminOrManager


class GitLabIntegrationView(APIView):
    """API view for GitLab integration."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='测试GitLab连接')
    def get(self, request):
        """Test GitLab connection."""
        service = GitLabService()
        result = service.test_connection()
        return Response(result)
    
    @extend_schema(description='获取GitLab项目列表')
    @action(detail=False, methods=['get'])
    def projects(self, request):
        """Get GitLab projects."""
        search = request.query_params.get('search')
        service = GitLabService()
        projects = service.get_projects(search=search)
        return Response(projects)


class GitLabProjectView(APIView):
    """API view for GitLab project operations."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取GitLab项目详情')
    def get(self, request, project_id):
        """Get GitLab project details."""
        service = GitLabService()
        project = service.get_project(int(project_id))
        if project:
            return Response(project)
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


class GitLabBranchesView(APIView):
    """API view for GitLab branches."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取GitLab项目分支列表')
    def get(self, request, project_id):
        """Get project branches."""
        service = GitLabService()
        branches = service.get_branches(int(project_id))
        return Response(branches)


class GitLabTagsView(APIView):
    """API view for GitLab tags."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取GitLab项目标签列表')
    def get(self, request, project_id):
        """Get project tags."""
        service = GitLabService()
        tags = service.get_tags(int(project_id))
        return Response(tags)


class ALMIntegrationView(APIView):
    """API view for ALM integration."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='测试ALM连接')
    def get(self, request):
        """Test ALM connection."""
        service = ALMService()
        result = service.test_connection()
        return Response(result)


class ALMTestSetsView(APIView):
    """API view for ALM test sets."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取ALM测试集列表')
    def get(self, request, project_id):
        """Get test sets for a project."""
        service = ALMService()
        test_sets = service.get_test_sets(project_id)
        return Response(test_sets)


class ALMTestCasesView(APIView):
    """API view for ALM test cases."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取ALM测试用例列表')
    def get(self, request, test_set_id):
        """Get test cases in a test set."""
        service = ALMService()
        test_cases = service.get_test_cases(test_set_id)
        return Response(test_cases)


class ALMSyncView(APIView):
    """API view for ALM sync operations."""
    permission_classes = [IsAdminOrManager]
    
    @extend_schema(description='同步ALM测试用例')
    def post(self, request):
        """Sync test cases from ALM."""
        project_id = request.data.get('project_id')
        test_set_id = request.data.get('test_set_id')
        task_id = request.data.get('task_id')
        
        if not all([project_id, test_set_id, task_id]):
            return Response(
                {'error': 'project_id, test_set_id and task_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .tasks import sync_alm_test_cases
        celery_task = sync_alm_test_cases.delay(project_id, test_set_id, task_id)
        
        return Response({
            'message': 'ALM同步任务已创建',
            'task_id': celery_task.id
        })


class ArtifactRepoIntegrationView(APIView):
    """API view for artifact repository integration."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='测试制品库连接')
    def get(self, request):
        """Test artifact repository connection."""
        service = ArtifactRepoService()
        result = service.test_connection()
        return Response(result)


class ArtifactRepoSearchView(APIView):
    """API view for searching artifacts."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='搜索制品')
    def get(self, request):
        """Search for artifacts."""
        repository = request.query_params.get('repository')
        group = request.query_params.get('group')
        name = request.query_params.get('name')
        version = request.query_params.get('version')
        
        if not repository:
            return Response(
                {'error': 'repository is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ArtifactRepoService()
        artifacts = service.search_artifacts(
            repository=repository,
            group=group,
            name=name,
            version=version
        )
        return Response(artifacts)


class ArtifactRepoVersionsView(APIView):
    """API view for artifact versions."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取制品版本列表')
    def get(self, request):
        """Get artifact versions."""
        repository = request.query_params.get('repository')
        group = request.query_params.get('group')
        artifact_id = request.query_params.get('artifact_id')
        
        if not all([repository, group, artifact_id]):
            return Response(
                {'error': 'repository, group and artifact_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ArtifactRepoService()
        versions = service.get_artifact_versions(repository, group, artifact_id)
        return Response({'versions': versions})
