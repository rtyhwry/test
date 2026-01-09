"""
Celery configuration for NEV Test Platform.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('nev_test_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Sync tasks from ALM every hour
    'sync-alm-tasks-hourly': {
        'task': 'apps.integrations.tasks.sync_alm_tasks',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
    # Check host status every 5 minutes
    'check-host-status': {
        'task': 'apps.hosts.tasks.check_all_hosts_status',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    # Clean up old logs daily
    'cleanup-old-logs': {
        'task': 'apps.tasks.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
    },
    # Release expired environment locks
    'release-expired-locks': {
        'task': 'apps.environments.tasks.release_expired_locks',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
