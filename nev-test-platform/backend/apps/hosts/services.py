"""Services for host management."""
import paramiko
import socket
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class HostConnectionService:
    """Service for managing SSH connections to hosts."""
    
    def __init__(self, host):
        """Initialize service with host model instance."""
        self.host = host
        self.client = None
    
    def _get_ssh_client(self) -> paramiko.SSHClient:
        """Create and configure SSH client."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client
    
    def connect(self, timeout: int = 10) -> bool:
        """Establish SSH connection to host."""
        try:
            self.client = self._get_ssh_client()
            
            connect_kwargs = {
                'hostname': self.host.ip_address,
                'port': self.host.ssh_port,
                'username': self.host.ssh_username,
                'timeout': timeout,
            }
            
            # Use SSH key if available, otherwise use password
            if self.host.ssh_key:
                import io
                key_file = io.StringIO(self.host.ssh_key)
                pkey = paramiko.RSAKey.from_private_key(key_file)
                connect_kwargs['pkey'] = pkey
            elif self.host.ssh_password:
                connect_kwargs['password'] = self.host.ssh_password
            
            self.client.connect(**connect_kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to host {self.host.name}: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command on remote host."""
        if not self.client:
            if not self.connect():
                return {'success': False, 'error': 'Failed to connect'}
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                'success': exit_code == 0,
                'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'exit_code': exit_code
            }
        except Exception as e:
            logger.error(f"Failed to execute command on {self.host.name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SSH connection and get basic info."""
        try:
            if self.connect():
                result = self.execute_command('hostname && uname -a')
                self.disconnect()
                
                if result['success']:
                    return {
                        'success': True,
                        'data': {
                            'hostname': result['stdout'].split('\n')[0],
                            'system_info': result['stdout'].split('\n')[1] if len(result['stdout'].split('\n')) > 1 else ''
                        }
                    }
                return {'success': False, 'error': result.get('error', 'Command failed')}
            return {'success': False, 'error': 'Connection failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.disconnect()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information from host."""
        try:
            if not self.connect():
                return {'error': 'Connection failed'}
            
            # Get CPU usage
            cpu_result = self.execute_command(
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
            )
            
            # Get memory usage
            mem_result = self.execute_command(
                "free | grep Mem | awk '{print $3/$2 * 100.0}'"
            )
            
            # Get disk usage
            disk_result = self.execute_command(
                "df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1"
            )
            
            # Get uptime
            uptime_result = self.execute_command("uptime -p")
            
            self.disconnect()
            
            return {
                'status': 'online',
                'cpu_usage': float(cpu_result['stdout'].strip()) if cpu_result['success'] else 0,
                'memory_usage': float(mem_result['stdout'].strip()) if mem_result['success'] else 0,
                'disk_usage': float(disk_result['stdout'].strip()) if disk_result['success'] else 0,
                'uptime': uptime_result['stdout'].strip() if uptime_result['success'] else 'Unknown',
            }
        except Exception as e:
            return {'error': str(e)}
        finally:
            self.disconnect()
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to remote host via SFTP."""
        try:
            if not self.connect():
                return False
            
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to {self.host.name}: {e}")
            return False
        finally:
            self.disconnect()
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from remote host via SFTP."""
        try:
            if not self.connect():
                return False
            
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return True
        except Exception as e:
            logger.error(f"Failed to download file from {self.host.name}: {e}")
            return False
        finally:
            self.disconnect()
