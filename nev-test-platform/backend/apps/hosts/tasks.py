"""Celery tasks for host management."""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_host_status(host_id: int):
    """Check status of a single host."""
    from .models import TestHost
    from .services import HostConnectionService
    
    try:
        host = TestHost.objects.get(id=host_id)
        service = HostConnectionService(host)
        
        result = service.test_connection()
        
        if result['success']:
            host.status = TestHost.Status.ONLINE
            host.last_heartbeat = timezone.now()
        else:
            host.status = TestHost.Status.OFFLINE
        
        host.save()
        
        return {
            'host_id': host_id,
            'status': host.status,
            'success': result['success']
        }
    except TestHost.DoesNotExist:
        logger.error(f"Host {host_id} not found")
        return {'error': f'Host {host_id} not found'}
    except Exception as e:
        logger.error(f"Error checking host {host_id}: {e}")
        return {'error': str(e)}


@shared_task
def check_all_hosts_status():
    """Check status of all hosts."""
    from .models import TestHost
    
    hosts = TestHost.objects.all()
    results = []
    
    for host in hosts:
        result = check_host_status.delay(host.id)
        results.append({
            'host_id': host.id,
            'task_id': result.id
        })
    
    return {
        'message': f'Started checking {len(results)} hosts',
        'tasks': results
    }
