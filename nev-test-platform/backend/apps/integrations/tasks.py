"""Celery tasks for integrations."""
from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_alm_tasks():
    """Sync tasks from ALM for all projects with ALM integration."""
    from apps.projects.models import Project
    from .services import ALMService
    
    projects = Project.objects.exclude(alm_project_id='')
    
    synced_count = 0
    for project in projects:
        try:
            service = ALMService()
            test_sets = service.get_test_sets(project.alm_project_id)
            
            for test_set in test_sets:
                # Sync each test set as a task
                # Implementation depends on ALM structure
                pass
            
            synced_count += 1
            logger.info(f"Synced ALM tasks for project {project.name}")
            
        except Exception as e:
            logger.error(f"Failed to sync ALM tasks for project {project.name}: {e}")
    
    return {'synced_projects': synced_count}


@shared_task
def sync_alm_test_cases(project_id: str, test_set_id: str, task_id: int):
    """Sync test cases from ALM to a specific task."""
    from apps.tasks.models import TestTask
    from apps.testcases.models import TestCase
    from .services import ALMService
    
    try:
        task = TestTask.objects.get(id=task_id)
        service = ALMService()
        
        # Get test cases from ALM
        alm_cases = service.sync_test_cases(project_id, test_set_id)
        
        created_count = 0
        updated_count = 0
        
        for case_data in alm_cases:
            test_case, created = TestCase.objects.update_or_create(
                task=task,
                alm_case_id=case_data['alm_case_id'],
                defaults={
                    'name': case_data['name'],
                    'case_code': case_data['case_code'],
                    'description': case_data['description'],
                    'priority': case_data['priority'],
                    'expected_result': case_data['expected_result'],
                    'preconditions': case_data['preconditions'],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Synced {created_count + updated_count} test cases for task {task_id}")
        
        return {
            'success': True,
            'created': created_count,
            'updated': updated_count
        }
        
    except TestTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'success': False, 'error': 'Task not found'}
    except Exception as e:
        logger.error(f"Failed to sync ALM test cases: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def sync_artifact_versions(repository: str, group: str = None, artifact_id: str = None):
    """Sync artifact versions from repository."""
    from apps.artifacts.models import Artifact
    from .services import ArtifactRepoService
    
    service = ArtifactRepoService()
    
    try:
        artifacts = service.search_artifacts(
            repository=repository,
            group=group,
            name=artifact_id
        )
        
        synced_count = 0
        for item in artifacts:
            try:
                # Parse artifact info from path
                path_parts = item.get('path', '').split('/')
                if len(path_parts) < 3:
                    continue
                
                name = path_parts[-3]
                version = path_parts[-2]
                file_name = path_parts[-1]
                
                Artifact.objects.update_or_create(
                    name=name,
                    version=version,
                    defaults={
                        'repository': repository,
                        'group_id': group or '',
                        'artifact_id': name,
                        'file_name': file_name,
                        'file_size': item.get('fileSize'),
                        'checksum': item.get('checksum', {}).get('sha256', ''),
                        'download_url': item.get('downloadUrl', ''),
                    }
                )
                synced_count += 1
                
            except Exception as e:
                logger.error(f"Failed to sync artifact: {e}")
        
        return {'success': True, 'synced': synced_count}
        
    except Exception as e:
        logger.error(f"Failed to sync artifacts: {e}")
        return {'success': False, 'error': str(e)}
