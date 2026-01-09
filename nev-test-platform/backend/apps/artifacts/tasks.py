"""Celery tasks for artifact management."""
from celery import shared_task
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_artifacts_from_repo(repository: str, group_id: str = None, 
                             artifact_id: str = None, version_pattern: str = None):
    """
    Sync artifacts from artifact repository.
    
    This task connects to the configured artifact repository (e.g., Nexus, Artifactory)
    and syncs available artifacts to the local database.
    """
    from .models import Artifact
    
    logger.info(f"Starting artifact sync from repository: {repository}")
    
    # Get repository credentials from settings
    repo_url = settings.ARTIFACT_REPO_URL
    username = settings.ARTIFACT_REPO_USERNAME
    password = settings.ARTIFACT_REPO_PASSWORD
    
    if not repo_url:
        logger.error("Artifact repository URL not configured")
        return {'error': 'Repository URL not configured'}
    
    synced_count = 0
    errors = []
    
    try:
        # Build search URL based on repository type
        # This is a generic implementation - adjust based on actual repository
        search_url = f"{repo_url}/service/rest/v1/search/assets"
        
        params = {
            'repository': repository,
        }
        if group_id:
            params['group'] = group_id
        if artifact_id:
            params['name'] = artifact_id
        
        # Make request to repository API
        auth = (username, password) if username else None
        response = requests.get(search_url, params=params, auth=auth, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch artifacts: {response.status_code}")
            return {'error': f'Repository returned status {response.status_code}'}
        
        data = response.json()
        items = data.get('items', [])
        
        for item in items:
            try:
                # Extract artifact info
                version = item.get('version', '')
                
                # Filter by version pattern if specified
                if version_pattern:
                    import re
                    if not re.match(version_pattern, version):
                        continue
                
                # Create or update artifact
                artifact, created = Artifact.objects.update_or_create(
                    name=item.get('name', ''),
                    version=version,
                    defaults={
                        'repository': repository,
                        'group_id': item.get('group', ''),
                        'artifact_id': item.get('name', ''),
                        'file_name': item.get('path', '').split('/')[-1],
                        'file_size': item.get('fileSize'),
                        'checksum': item.get('checksum', {}).get('sha256', ''),
                        'download_url': item.get('downloadUrl', ''),
                    }
                )
                
                if created:
                    synced_count += 1
                    logger.info(f"Synced artifact: {artifact.name} v{artifact.version}")
                    
            except Exception as e:
                logger.error(f"Error syncing artifact: {e}")
                errors.append(str(e))
        
        return {
            'synced_count': synced_count,
            'total_found': len(items),
            'errors': errors
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during artifact sync: {e}")
        return {'error': str(e)}
    except Exception as e:
        logger.error(f"Error during artifact sync: {e}")
        return {'error': str(e)}


@shared_task
def download_artifact(artifact_id: int):
    """Download artifact file to local storage."""
    from .models import Artifact
    import os
    import hashlib
    
    try:
        artifact = Artifact.objects.get(id=artifact_id)
        
        # Create download directory
        download_dir = settings.UPLOAD_DIR / 'artifacts'
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Download file
        local_path = download_dir / artifact.file_name
        
        logger.info(f"Downloading artifact {artifact.name} v{artifact.version}")
        
        response = requests.get(artifact.download_url, stream=True, timeout=600)
        response.raise_for_status()
        
        sha256 = hashlib.sha256()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                sha256.update(chunk)
        
        # Verify checksum if available
        if artifact.checksum:
            calculated_checksum = sha256.hexdigest()
            if calculated_checksum != artifact.checksum:
                os.remove(local_path)
                logger.error(f"Checksum mismatch for artifact {artifact_id}")
                return {'error': 'Checksum mismatch'}
        
        # Update local path
        artifact.local_path = str(local_path)
        artifact.save()
        
        logger.info(f"Successfully downloaded artifact to {local_path}")
        
        return {
            'artifact_id': artifact_id,
            'local_path': str(local_path),
            'file_size': os.path.getsize(local_path)
        }
        
    except Artifact.DoesNotExist:
        return {'error': f'Artifact {artifact_id} not found'}
    except Exception as e:
        logger.error(f"Error downloading artifact {artifact_id}: {e}")
        return {'error': str(e)}
