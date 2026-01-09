"""GitLab integration service."""
import gitlab
from django.conf import settings
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class GitLabService:
    """Service for GitLab integration."""
    
    def __init__(self, url: str = None, token: str = None):
        """Initialize GitLab service."""
        self.url = url or settings.GITLAB_URL
        self.token = token or settings.GITLAB_TOKEN
        self._client = None
    
    @property
    def client(self):
        """Get GitLab client (lazy initialization)."""
        if self._client is None:
            if not self.url or not self.token:
                raise ValueError("GitLab URL and token are required")
            self._client = gitlab.Gitlab(self.url, private_token=self.token)
        return self._client
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitLab connection."""
        try:
            self.client.auth()
            user = self.client.user
            return {
                'success': True,
                'user': user.username,
                'name': user.name
            }
        except Exception as e:
            logger.error(f"GitLab connection test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_projects(self, search: str = None, limit: int = 20) -> List[Dict]:
        """Get list of projects."""
        try:
            if search:
                projects = self.client.projects.list(search=search, per_page=limit)
            else:
                projects = self.client.projects.list(per_page=limit)
            
            return [
                {
                    'id': p.id,
                    'name': p.name,
                    'path': p.path_with_namespace,
                    'url': p.web_url,
                    'default_branch': p.default_branch
                }
                for p in projects
            ]
        except Exception as e:
            logger.error(f"Failed to get GitLab projects: {e}")
            return []
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project details."""
        try:
            project = self.client.projects.get(project_id)
            return {
                'id': project.id,
                'name': project.name,
                'path': project.path_with_namespace,
                'url': project.web_url,
                'default_branch': project.default_branch,
                'description': project.description
            }
        except Exception as e:
            logger.error(f"Failed to get GitLab project {project_id}: {e}")
            return None
    
    def get_branches(self, project_id: int) -> List[Dict]:
        """Get project branches."""
        try:
            project = self.client.projects.get(project_id)
            branches = project.branches.list(per_page=100)
            return [
                {
                    'name': b.name,
                    'commit': b.commit['id'][:8],
                    'protected': b.protected
                }
                for b in branches
            ]
        except Exception as e:
            logger.error(f"Failed to get branches for project {project_id}: {e}")
            return []
    
    def get_tags(self, project_id: int) -> List[Dict]:
        """Get project tags."""
        try:
            project = self.client.projects.get(project_id)
            tags = project.tags.list(per_page=100)
            return [
                {
                    'name': t.name,
                    'commit': t.commit['id'][:8],
                    'message': t.message
                }
                for t in tags
            ]
        except Exception as e:
            logger.error(f"Failed to get tags for project {project_id}: {e}")
            return []
    
    def get_file_content(self, project_id: int, file_path: str, 
                        ref: str = 'main') -> Optional[str]:
        """Get file content from repository."""
        try:
            project = self.client.projects.get(project_id)
            file = project.files.get(file_path=file_path, ref=ref)
            return file.decode().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to get file {file_path} from project {project_id}: {e}")
            return None
    
    def trigger_pipeline(self, project_id: int, ref: str, 
                        variables: Dict[str, str] = None) -> Optional[Dict]:
        """Trigger CI/CD pipeline."""
        try:
            project = self.client.projects.get(project_id)
            pipeline = project.pipelines.create({
                'ref': ref,
                'variables': [
                    {'key': k, 'value': v}
                    for k, v in (variables or {}).items()
                ]
            })
            return {
                'id': pipeline.id,
                'status': pipeline.status,
                'web_url': pipeline.web_url
            }
        except Exception as e:
            logger.error(f"Failed to trigger pipeline: {e}")
            return None
