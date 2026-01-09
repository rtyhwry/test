"""ALM (Application Lifecycle Management) integration service."""
import requests
from django.conf import settings
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ALMService:
    """Service for ALM integration (e.g., HP ALM, Jira, Azure DevOps)."""
    
    def __init__(self, url: str = None, username: str = None, password: str = None):
        """Initialize ALM service."""
        self.url = url or settings.ALM_URL
        self.username = username or settings.ALM_USERNAME
        self.password = password or settings.ALM_PASSWORD
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
        """Test ALM connection."""
        try:
            response = self.session.get(f"{self.url}/api/v1/ping", timeout=10)
            if response.status_code == 200:
                return {'success': True}
            return {'success': False, 'error': f'Status code: {response.status_code}'}
        except Exception as e:
            logger.error(f"ALM connection test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_test_sets(self, project_id: str) -> List[Dict]:
        """Get test sets for a project."""
        try:
            response = self.session.get(
                f"{self.url}/api/v1/projects/{project_id}/test-sets",
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to get test sets: {e}")
            return []
    
    def get_test_cases(self, test_set_id: str) -> List[Dict]:
        """Get test cases in a test set."""
        try:
            response = self.session.get(
                f"{self.url}/api/v1/test-sets/{test_set_id}/test-cases",
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to get test cases: {e}")
            return []
    
    def get_test_case(self, case_id: str) -> Optional[Dict]:
        """Get test case details."""
        try:
            response = self.session.get(
                f"{self.url}/api/v1/test-cases/{case_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get test case {case_id}: {e}")
            return None
    
    def create_test_run(self, test_set_id: str, name: str, 
                       environment: str = None) -> Optional[Dict]:
        """Create a new test run."""
        try:
            data = {
                'test_set_id': test_set_id,
                'name': name,
                'environment': environment
            }
            response = self.session.post(
                f"{self.url}/api/v1/test-runs",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create test run: {e}")
            return None
    
    def update_test_result(self, run_id: str, case_id: str, 
                          status: str, details: Dict = None) -> bool:
        """Update test case result in ALM."""
        try:
            data = {
                'status': status,  # passed, failed, blocked, etc.
                'details': details or {}
            }
            response = self.session.put(
                f"{self.url}/api/v1/test-runs/{run_id}/results/{case_id}",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update test result: {e}")
            return False
    
    def sync_test_cases(self, project_id: str, test_set_id: str) -> List[Dict]:
        """
        Sync test cases from ALM to local database.
        
        Returns list of test case data ready to be imported.
        """
        cases = self.get_test_cases(test_set_id)
        
        synced_cases = []
        for case in cases:
            synced_cases.append({
                'alm_case_id': case.get('id'),
                'name': case.get('name'),
                'case_code': case.get('code', f"ALM_{case.get('id')}"),
                'description': case.get('description', ''),
                'priority': self._map_priority(case.get('priority')),
                'expected_result': case.get('expected_result', ''),
                'preconditions': case.get('preconditions', ''),
            })
        
        return synced_cases
    
    def _map_priority(self, alm_priority: str) -> str:
        """Map ALM priority to internal priority."""
        priority_map = {
            '1': 'critical',
            '2': 'high',
            '3': 'medium',
            '4': 'low',
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        return priority_map.get(str(alm_priority).lower(), 'medium')
