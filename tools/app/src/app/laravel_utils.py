import subprocess
import time
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class LaravelUtils:
    """Laravel-specific utility functions."""
    
    PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
    
    @classmethod
    def get_laravel_env_path(cls) -> Path:
        """Find .env file location in project root."""
        env_path = cls.PROJECT_ROOT / ".env"
        return env_path
    
    @classmethod
    def validate_laravel_project(cls) -> bool:
        """Ensure we're in a Laravel project directory."""
        required_files = ['artisan', 'composer.json', 'app', 'bootstrap']
        for file in required_files:
            if not (cls.PROJECT_ROOT / file).exists():
                return False
        return True
    
    @classmethod
    def get_laravel_config(cls, key: str) -> Any:
        """Read Laravel config values using artisan."""
        from .service_discovery import ServiceDiscovery
        
        php_container = ServiceDiscovery.get_php_container()
        if not php_container:
            return None
        
        try:
            result = subprocess.run(
                ['docker', 'exec', php_container, 'php', 'artisan', 'tinker', '--execute', f"config('{key}')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse output - it's usually in format: => "value"
                output = result.stdout.strip()
                if '=>' in output:
                    value = output.split('=>', 1)[1].strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    return value
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        
        return None
    
    @classmethod
    def detect_laravel_version(cls) -> str:
        """Detect Laravel version for version-specific behavior."""
        composer_lock = cls.PROJECT_ROOT / "composer.lock"
        if not composer_lock.exists():
            return "unknown"
        
        try:
            import json
            with open(composer_lock, 'r') as f:
                data = json.load(f)
                for package in data.get('packages', []):
                    if package.get('name') == 'laravel/framework':
                        version = package.get('version', 'unknown')
                        # Extract major version
                        if version.startswith('v'):
                            version = version[1:]
                        if '.' in version:
                            return version.split('.')[0]
                        return version
        except Exception:
            pass
        
        return "unknown"
    
    @classmethod
    def has_artisan_command(cls, command: str) -> bool:
        """Check if artisan command exists."""
        from .service_discovery import ServiceDiscovery
        
        php_container = ServiceDiscovery.get_php_container()
        if not php_container:
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'exec', php_container, 'php', 'artisan', 'list', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0 and command in result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    @classmethod
    def wait_for_database(cls, timeout: int = 60) -> bool:
        """Wait for database to be ready."""
        from .database_utils import DatabaseUtils
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if DatabaseUtils.test_mysql_connection(DatabaseUtils.get_mysql_credentials()):
                return True
            time.sleep(2)
        
        return False
    
    @classmethod
    def wait_for_services(cls, services: List[str], timeout: int = 60) -> bool:
        """Wait for services to be ready."""
        from .service_discovery import ServiceDiscovery
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_ready = True
            
            for service in services:
                container_name = f"customer-dashboard-{service}"
                
                # Check if container is running
                try:
                    result = subprocess.run(
                        ['docker', 'inspect', '-f', '{{.State.Running}}', container_name],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0 or result.stdout.strip() != 'true':
                        all_ready = False
                        break
                except subprocess.CalledProcessError:
                    all_ready = False
                    break
            
            if all_ready:
                # Extra wait for services to be fully ready
                time.sleep(2)
                return True
            
            time.sleep(2)
        
        return False
    
    @classmethod
    def generate_app_key(cls) -> bool:
        """Generate Laravel application key if missing."""
        from .service_discovery import ServiceDiscovery
        
        php_container = ServiceDiscovery.get_php_container()
        if not php_container:
            return False
        
        try:
            result = subprocess.run(
                ['docker', 'exec', php_container, 'php', 'artisan', 'key:generate'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    @classmethod
    def check_env_file(cls) -> Dict[str, Any]:
        """Validate .env file has required keys."""
        env_path = cls.get_laravel_env_path()
        
        result = {
            'exists': env_path.exists(),
            'missing_keys': [],
            'has_app_key': False
        }
        
        if not result['exists']:
            result['missing_keys'] = ['ALL']
            return result
        
        required_keys = [
            'APP_NAME',
            'APP_ENV',
            'APP_KEY',
            'APP_DEBUG',
            'APP_URL',
            'DB_CONNECTION',
            'DB_HOST',
            'DB_PORT',
            'DB_DATABASE',
            'DB_USERNAME',
            'DB_PASSWORD'
        ]
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                
                for key in required_keys:
                    if f'{key}=' not in content:
                        result['missing_keys'].append(key)
                
                # Check if APP_KEY has a value
                if 'APP_KEY=' in content:
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('APP_KEY='):
                            value = line.split('=', 1)[1].strip()
                            if value and value != '':
                                result['has_app_key'] = True
                            break
        except IOError:
            result['missing_keys'] = ['ERROR_READING_FILE']
        
        return result
    
    @classmethod
    def run_artisan_command(cls, command: str, container: str = None) -> subprocess.CompletedProcess:
        """Execute artisan command in appropriate container."""
        from .service_discovery import ServiceDiscovery
        
        if not container:
            container = ServiceDiscovery.get_php_container()
            if not container:
                raise RuntimeError("No PHP container running")
        
        cmd_parts = command.split()
        cmd = ['docker', 'exec', container, 'php', 'artisan'] + cmd_parts
        
        return subprocess.run(cmd, capture_output=True, text=True)
    
    @classmethod
    def check_storage_link(cls) -> bool:
        """Check if storage link exists and is valid."""
        public_storage = cls.PROJECT_ROOT / "public" / "storage"
        storage_app_public = cls.PROJECT_ROOT / "storage" / "app" / "public"
        
        if not public_storage.exists():
            return False
        
        if public_storage.is_symlink():
            # Check if symlink points to correct location
            try:
                target = public_storage.resolve()
                return target == storage_app_public
            except Exception:
                return False
        
        return False
    
    @classmethod
    def get_composer_lock_hash(cls) -> str:
        """Get hash of composer.lock for dependency change detection."""
        composer_lock = cls.PROJECT_ROOT / "composer.lock"
        
        if not composer_lock.exists():
            return ""
        
        try:
            with open(composer_lock, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except IOError:
            return ""
    
    @classmethod
    def clear_laravel_queues(cls, stack_name: str) -> None:
        """Clear all Laravel queues for a stack."""
        from .service_discovery import ServiceDiscovery
        
        php_container = ServiceDiscovery.get_php_container()
        if php_container:
            try:
                subprocess.run(
                    ['docker', 'exec', php_container, 'php', 'artisan', 'queue:clear'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass
    
    @classmethod
    def optimize_laravel_caches(cls, stack_name: str) -> None:
        """Clear and optimize Laravel caches."""
        from .service_discovery import ServiceDiscovery
        
        php_container = ServiceDiscovery.get_php_container()
        if php_container:
            try:
                # Clear first
                subprocess.run(
                    ['docker', 'exec', php_container, 'php', 'artisan', 'optimize:clear'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Then optimize
                subprocess.run(
                    ['docker', 'exec', php_container, 'php', 'artisan', 'optimize'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass