"""Artifact repository integration service."""
import requests
from django.conf import settings
from typing import Dict, Any, List, Optional
import logging
import hashlib
import os

logger = logging.getLogger(__name__)


class ArtifactRepoService:
    """Service for artifact repository integration (Nexus, Artifactory, etc.)."""
    
    def __init__(self, url: str = None, username: str = None, password: str = None):
        """Initialize artifact repository service."""
        self.url = url or settings.ARTIFACT_REPO_URL
        self.username = username or settings.ARTIFACT_REPO_USERNAME
        self.password = password or settings.ARTIFACT_REPO_PASSWORD
        self._session = None
    
    @property
    def session(self):
        """Get authenticated session."""
        if self._session is None:
            self._session = requests.Session()
            if self.username and self.password:
                self._session.auth = (self.username, self.password)
        return self._session
    
    def test_connection(self) -> Dict[str, Any]:
        """Test repository connection."""
        try:
            response = self.session.get(
                f"{self.url}/service/rest/v1/status",
                timeout=10
            )
            if response.status_code == 200:
                return {'success': True}
            return {'success': False, 'error': f'Status code: {response.status_code}'}
        except Exception as e:
            logger.error(f"Artifact repo connection test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_repositories(self) -> List[Dict]:
        """Get list of repositories."""
        try:
            response = self.session.get(
                f"{self.url}/service/rest/v1/repositories",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get repositories: {e}")
            return []
    
    def search_artifacts(self, repository: str, group: str = None,
                        name: str = None, version: str = None) -> List[Dict]:
        """Search for artifacts."""
        try:
            params = {'repository': repository}
            if group:
                params['group'] = group
            if name:
                params['name'] = name
            if version:
                params['version'] = version
            
            response = self.session.get(
                f"{self.url}/service/rest/v1/search/assets",
                params=params,
                timeout=60
            )
            response.raise_for_status()
            
            items = response.json().get('items', [])
            return [
                {
                    'id': item.get('id'),
                    'path': item.get('path'),
                    'repository': item.get('repository'),
                    'format': item.get('format'),
                    'checksum': item.get('checksum', {}),
                    'downloadUrl': item.get('downloadUrl'),
                    'fileSize': item.get('fileSize')
                }
                for item in items
            ]
        except Exception as e:
            logger.error(f"Failed to search artifacts: {e}")
            return []
    
    def get_artifact_versions(self, repository: str, group: str, 
                             artifact_id: str) -> List[str]:
        """Get available versions for an artifact."""
        try:
            artifacts = self.search_artifacts(
                repository=repository,
                group=group,
                name=artifact_id
            )
            
            versions = set()
            for artifact in artifacts:
                path = artifact.get('path', '')
                # Extract version from path (assuming Maven-like structure)
                parts = path.split('/')
                if len(parts) >= 2:
                    versions.add(parts[-2])
            
            return sorted(list(versions), reverse=True)
        except Exception as e:
            logger.error(f"Failed to get artifact versions: {e}")
            return []
    
    def download_artifact(self, download_url: str, 
                         local_path: str, 
                         expected_checksum: str = None) -> Dict[str, Any]:
        """Download artifact to local path."""
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            response = self.session.get(download_url, stream=True, timeout=600)
            response.raise_for_status()
            
            sha256 = hashlib.sha256()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    sha256.update(chunk)
            
            actual_checksum = sha256.hexdigest()
            
            # Verify checksum if provided
            if expected_checksum and actual_checksum != expected_checksum:
                os.remove(local_path)
                return {
                    'success': False,
                    'error': f'Checksum mismatch: expected {expected_checksum}, got {actual_checksum}'
                }
            
            return {
                'success': True,
                'local_path': local_path,
                'checksum': actual_checksum,
                'size': os.path.getsize(local_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to download artifact: {e}")
            if os.path.exists(local_path):
                os.remove(local_path)
            return {'success': False, 'error': str(e)}
    
    def get_latest_version(self, repository: str, group: str, 
                          artifact_id: str) -> Optional[Dict]:
        """Get latest version of an artifact."""
        try:
            versions = self.get_artifact_versions(repository, group, artifact_id)
            if not versions:
                return None
            
            latest_version = versions[0]  # Versions are sorted in descending order
            
            artifacts = self.search_artifacts(
                repository=repository,
                group=group,
                name=artifact_id,
                version=latest_version
            )
            
            return artifacts[0] if artifacts else None
            
        except Exception as e:
            logger.error(f"Failed to get latest version: {e}")
            return None
