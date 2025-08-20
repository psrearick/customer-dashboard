import subprocess
import os
from pathlib import Path
from typing import Dict, Optional
import re


class DatabaseUtils:
    """Database credential discovery and connection utilities."""
    
    PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
    ENV_FILE = PROJECT_ROOT / ".env"
    
    @classmethod
    def get_mysql_credentials(cls) -> Dict[str, str]:
        """Discover MySQL credentials from .env and container environment."""
        credentials = {
            'host': 'localhost',
            'port': '3306',
            'username': 'laravel',
            'password': 'password',
            'database': 'laravel_perf'
        }
        
        env_vars = cls.parse_laravel_env()
        if env_vars:
            credentials['host'] = env_vars.get('DB_HOST', 'localhost')
            credentials['port'] = env_vars.get('DB_PORT', '3306')
            credentials['username'] = env_vars.get('DB_USERNAME', 'laravel')
            credentials['password'] = env_vars.get('DB_PASSWORD', 'password')
            credentials['database'] = env_vars.get('DB_DATABASE', 'laravel_perf')
        
        # Container names need localhost mapping for external access
        if credentials['host'] in ['mysql', 'customer-dashboard-mysql']:
            container_env = cls.query_container_env('customer-dashboard-mysql')
            if container_env:
                credentials['host'] = 'localhost'
                credentials['password'] = container_env.get('MYSQL_PASSWORD', credentials['password'])
                credentials['database'] = container_env.get('MYSQL_DATABASE', credentials['database'])
        
        return credentials
    
    @classmethod
    def get_redis_credentials(cls) -> Dict[str, str]:
        """Discover Redis credentials and connection info."""
        credentials = {
            'host': 'localhost',
            'port': '6379',
            'password': None,
            'database': '0'
        }
        
        env_vars = cls.parse_laravel_env()
        if env_vars:
            credentials['host'] = env_vars.get('REDIS_HOST', 'localhost')
            credentials['port'] = env_vars.get('REDIS_PORT', '6379')
            credentials['password'] = env_vars.get('REDIS_PASSWORD')
            
            cache_db = env_vars.get('REDIS_CACHE_DB', '1')
            credentials['database'] = cache_db
        
        # Container names need localhost mapping for external access
        if credentials['host'] in ['redis', 'customer-dashboard-redis']:
            credentials['host'] = 'localhost'
        
        return credentials
    
    @classmethod
    def parse_laravel_env(cls) -> Dict[str, str]:
        """Parse .env file in project root."""
        env_vars = {}
        
        if not cls.ENV_FILE.exists():
            return env_vars
        
        try:
            with open(cls.ENV_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        env_vars[key] = value
        except IOError:
            pass
        
        return env_vars
    
    @classmethod
    def query_container_env(cls, container_name: str) -> Dict[str, str]:
        """Get environment variables from running container."""
        env_vars = {}
        
        try:
            result = subprocess.run(
                ['docker', 'inspect', container_name, '--format', '{{range .Config.Env}}{{println .}}{{end}}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        except subprocess.CalledProcessError:
            pass
        
        return env_vars
    
    @classmethod
    def get_database_connection_string(cls, credentials: Dict) -> str:
        """Generate connection string for mysql command."""
        return (
            f"-h {credentials['host']} "
            f"-P {credentials['port']} "
            f"-u {credentials['username']} "
            f"{credentials['database']}"
        )
    
    @classmethod
    def test_mysql_connection(cls, credentials: Dict) -> bool:
        """Test MySQL connection with given credentials."""
        try:
            result = subprocess.run(
                [
                    'docker', 'run', '--rm', '--network=customer-dashboard',
                    'mysql:8.4',
                    'mysql',
                    '-h', credentials['host'],
                    '-P', credentials['port'],
                    '-u', credentials['username'],
                    f"-p{credentials['password']}",
                    '-e', 'SELECT 1'
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    @classmethod
    def test_redis_connection(cls, credentials: Dict) -> bool:
        """Test Redis connection."""
        try:
            cmd = ['redis-cli', '-h', credentials['host'], '-p', credentials['port']]
            
            if credentials.get('password'):
                cmd.extend(['-a', credentials['password']])
            
            cmd.extend(['ping'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            return 'PONG' in result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @classmethod
    def get_mysql_root_credentials(cls) -> Dict[str, str]:
        """Get MySQL root credentials."""
        credentials = cls.get_mysql_credentials()
        
        # Try to get root password from container
        container_env = cls.query_container_env('customer-dashboard-mysql')
        if container_env:
            credentials['username'] = 'root'
            credentials['password'] = container_env.get('MYSQL_ROOT_PASSWORD', 'rootpassword')
        else:
            # Fallback to common defaults
            credentials['username'] = 'root'
            credentials['password'] = 'rootpassword'
        
        return credentials