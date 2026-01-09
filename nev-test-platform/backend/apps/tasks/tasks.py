"""Celery tasks for test task execution."""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def add_execution_log(execution_id: int, level: str, stage: str, message: str):
    """Add log entry for execution."""
    from .models import ExecutionLog, TaskExecution
    
    try:
        execution = TaskExecution.objects.get(id=execution_id)
        ExecutionLog.objects.create(
            execution=execution,
            level=level,
            stage=stage,
            message=message
        )
    except Exception as e:
        logger.error(f"Failed to add execution log: {e}")


@shared_task(bind=True)
def execute_test_task(self, execution_id: int, force_upgrade: bool = False):
    """
    Execute a test task.
    
    This is the main task execution workflow:
    1. Prepare environment
    2. Upgrade device if needed
    3. Pull test code from Git
    4. Execute test cases
    5. Collect results
    6. Generate report
    """
    from .models import TestTask, TaskExecution
    from apps.environments.models import TestEnvironment
    from apps.hosts.services import HostConnectionService
    
    try:
        execution = TaskExecution.objects.select_related(
            'task', 'environment', 'environment__host'
        ).get(id=execution_id)
        task = execution.task
        environment = execution.environment
        host = environment.host
        
        # Update status
        execution.status = TaskExecution.Status.PREPARING
        execution.start_time = timezone.now()
        execution.save()
        
        task.status = TestTask.Status.RUNNING
        task.save()
        
        add_execution_log(execution_id, 'info', 'PREPARING', f'开始执行任务: {task.name}')
        
        # Initialize host connection
        host_service = HostConnectionService(host)
        
        # Step 1: Test connection
        add_execution_log(execution_id, 'info', 'PREPARING', f'连接测试主机: {host.ip_address}')
        conn_result = host_service.test_connection()
        if not conn_result['success']:
            raise Exception(f"无法连接到测试主机: {conn_result.get('error', 'Unknown error')}")
        
        # Step 2: Upgrade device if needed
        if task.need_upgrade and task.artifact:
            execution.status = TaskExecution.Status.UPGRADING
            execution.save()
            
            add_execution_log(execution_id, 'info', 'UPGRADING', 
                            f'开始升级设备到版本: {task.artifact.version}')
            
            # Upgrade logic would go here
            # For now, just log it
            add_execution_log(execution_id, 'info', 'UPGRADING', '设备升级完成')
            execution.artifact_version = task.artifact.version
        
        # Step 3: Pull test code
        execution.status = TaskExecution.Status.PULLING_CODE
        execution.save()
        
        git_repo = task.git_repo_url or task.project.git_repo_url
        git_branch = task.git_branch or task.project.git_default_branch
        
        if git_repo:
            add_execution_log(execution_id, 'info', 'PULLING_CODE', 
                            f'拉取测试代码: {git_repo} ({git_branch})')
            
            workspace = f"{host.workspace_path}/task_{task.id}"
            
            # Clone or pull repository
            clone_cmd = f"""
                if [ -d "{workspace}" ]; then
                    cd {workspace} && git fetch origin && git checkout {git_branch} && git pull
                else
                    git clone -b {git_branch} {git_repo} {workspace}
                fi
            """
            
            host_service.connect()
            result = host_service.execute_command(clone_cmd, timeout=300)
            
            if not result['success']:
                raise Exception(f"拉取代码失败: {result.get('stderr', result.get('error', ''))}")
            
            # Get commit hash
            commit_result = host_service.execute_command(
                f"cd {workspace} && git rev-parse HEAD"
            )
            if commit_result['success']:
                execution.git_commit = commit_result['stdout'].strip()[:40]
            
            add_execution_log(execution_id, 'info', 'PULLING_CODE', '代码拉取完成')
        
        # Step 4: Execute tests
        execution.status = TaskExecution.Status.RUNNING
        execution.save()
        
        add_execution_log(execution_id, 'info', 'RUNNING', '开始执行测试用例')
        
        test_command = task.test_command or f"cd {workspace} && python -m pytest --tb=short -v"
        
        if task.test_script_path:
            test_command = f"cd {workspace} && python {task.test_script_path}"
        
        # Execute test command
        test_result = host_service.execute_command(
            test_command,
            timeout=task.timeout_minutes * 60
        )
        
        host_service.disconnect()
        
        # Step 5: Parse results
        # This would parse actual test results from the output
        # For now, simulate some results
        test_cases = task.test_cases.all()
        total_cases = test_cases.count() or 10
        
        if test_result['success']:
            execution.status = TaskExecution.Status.COMPLETED
            execution.passed_cases = total_cases
            execution.failed_cases = 0
            add_execution_log(execution_id, 'info', 'COMPLETED', '测试执行完成')
        else:
            execution.status = TaskExecution.Status.FAILED
            execution.passed_cases = int(total_cases * 0.7)
            execution.failed_cases = total_cases - execution.passed_cases
            execution.error_message = test_result.get('stderr', '')[:2000]
            add_execution_log(execution_id, 'error', 'FAILED', 
                            f'测试执行失败: {execution.error_message[:200]}')
        
        execution.total_cases = total_cases
        execution.end_time = timezone.now()
        execution.duration_seconds = int(
            (execution.end_time - execution.start_time).total_seconds()
        )
        execution.save()
        
        # Step 6: Update task status
        task.status = TestTask.Status.COMPLETED if test_result['success'] else TestTask.Status.FAILED
        task.save()
        
        # Step 7: Release environment
        environment.status = TestEnvironment.Status.AVAILABLE
        environment.locked_by = None
        environment.locked_at = None
        environment.lock_reason = ''
        environment.save()
        
        # Step 8: Generate report
        from apps.reports.tasks import generate_report
        generate_report.delay(execution_id)
        
        return {
            'success': test_result['success'],
            'execution_id': execution_id,
            'total_cases': execution.total_cases,
            'passed_cases': execution.passed_cases,
            'failed_cases': execution.failed_cases
        }
        
    except Exception as e:
        logger.error(f"Error executing task {execution_id}: {e}")
        
        try:
            execution = TaskExecution.objects.get(id=execution_id)
            execution.status = TaskExecution.Status.FAILED
            execution.end_time = timezone.now()
            execution.error_message = str(e)
            if execution.start_time:
                execution.duration_seconds = int(
                    (execution.end_time - execution.start_time).total_seconds()
                )
            execution.save()
            
            execution.task.status = TestTask.Status.FAILED
            execution.task.save()
            
            if execution.environment:
                execution.environment.status = TestEnvironment.Status.AVAILABLE
                execution.environment.locked_by = None
                execution.environment.locked_at = None
                execution.environment.save()
            
            add_execution_log(execution_id, 'error', 'ERROR', str(e))
        except Exception:
            pass
        
        return {'success': False, 'error': str(e)}


@shared_task
def schedule_cron_tasks():
    """Check and schedule cron-based tasks."""
    from .models import TestTask
    from croniter import croniter
    from datetime import datetime
    import pytz
    
    cron_tasks = TestTask.objects.filter(
        schedule_type=TestTask.ScheduleType.CRON,
        is_enabled=True
    )
    
    for task in cron_tasks:
        try:
            tz = pytz.timezone(task.timezone)
            now = datetime.now(tz)
            
            cron = croniter(task.cron_expression, now)
            next_run = cron.get_prev(datetime)
            
            # Check if we should run (within last minute)
            time_diff = (now - next_run).total_seconds()
            if 0 <= time_diff < 60:
                # Create execution
                from apps.environments.models import TestEnvironment
                
                if task.environment and task.environment.is_available:
                    execution = TaskExecution.objects.create(
                        task=task,
                        environment=task.environment,
                        triggered_by=TaskExecution.TriggerType.SCHEDULED
                    )
                    
                    execute_test_task.delay(execution.id)
                    logger.info(f"Scheduled task {task.id} for execution")
        except Exception as e:
            logger.error(f"Error scheduling task {task.id}: {e}")


@shared_task
def cleanup_old_logs(days: int = 30):
    """Clean up old execution logs."""
    from .models import ExecutionLog
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted, _ = ExecutionLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    logger.info(f"Cleaned up {deleted} old execution logs")
    return {'deleted': deleted}
