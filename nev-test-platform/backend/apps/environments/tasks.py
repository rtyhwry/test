"""Celery tasks for environment management."""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def release_expired_locks():
    """Release environments with expired locks."""
    from .models import TestEnvironment
    
    now = timezone.now()
    
    # Find environments with expired locks
    expired_environments = TestEnvironment.objects.filter(
        status=TestEnvironment.Status.LOCKED,
        is_auto_release=True,
        lock_expires_at__lt=now
    )
    
    released_count = 0
    for env in expired_environments:
        logger.info(f"Auto-releasing expired lock on environment {env.name}")
        env.status = TestEnvironment.Status.AVAILABLE
        env.locked_by = None
        env.locked_at = None
        env.lock_reason = ''
        env.lock_expires_at = None
        env.save()
        released_count += 1
    
    return {
        'released_count': released_count,
        'timestamp': str(now)
    }


@shared_task
def check_environment_status(environment_id: int):
    """Check and update environment status based on host and devices."""
    from .models import TestEnvironment
    from apps.hosts.models import TestHost
    
    try:
        env = TestEnvironment.objects.get(id=environment_id)
        
        # Check host status
        host_online = env.host.status == TestHost.Status.ONLINE
        
        # Check device status
        all_devices_available = all(
            device.status in ['available', 'in_use']
            for device in env.devices.all()
        )
        
        # Update environment status if needed
        if not host_online:
            if env.status not in [TestEnvironment.Status.OFFLINE, TestEnvironment.Status.MAINTENANCE]:
                env.status = TestEnvironment.Status.OFFLINE
                env.save()
        elif not all_devices_available:
            if env.status not in [TestEnvironment.Status.MAINTENANCE, TestEnvironment.Status.LOCKED]:
                env.status = TestEnvironment.Status.MAINTENANCE
                env.save()
        
        return {
            'environment_id': environment_id,
            'status': env.status,
            'host_online': host_online,
            'devices_available': all_devices_available
        }
        
    except TestEnvironment.DoesNotExist:
        return {'error': f'Environment {environment_id} not found'}
