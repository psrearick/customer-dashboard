import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache


class StackConfig:
    """Stack configuration management and metadata retrieval."""
    
    PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
    STACK_DIR = PROJECT_ROOT / "docker" / "stacks"
    SERVICE_DIR = PROJECT_ROOT / "docker" / "services"
    
    @classmethod
    @lru_cache(maxsize=32)
    def load_stack_config(cls, stack_name: str) -> Dict:
        """Load and parse stack configuration from YAML file."""
        stack_file = cls.STACK_DIR / f"{stack_name}.yml"
        if not stack_file.exists():
            raise FileNotFoundError(f"Stack '{stack_name}' not found at {stack_file}")
        
        with open(stack_file, 'r') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def get_stack_access_url(cls, stack_name: str) -> str:
        """Get the primary access URL for a stack."""
        try:
            config = cls.load_stack_config(stack_name)
            return config.get('access_url', 'http://localhost')
        except FileNotFoundError:
            return 'http://localhost'
    
    @classmethod
    def get_stack_requirements(cls, stack_name: str) -> Dict:
        """Get resource requirements for a stack."""
        try:
            config = cls.load_stack_config(stack_name)
            return config.get('requirements', {
                'min_memory': '2GB',
                'ports': [],
                'features': []
            })
        except FileNotFoundError:
            return {'min_memory': '2GB', 'ports': [], 'features': []}
    
    @classmethod
    def get_stack_services(cls, stack_name: str) -> List[str]:
        """Get list of service names for a stack."""
        try:
            config = cls.load_stack_config(stack_name)
            return config.get('services', [])
        except FileNotFoundError:
            return []
    
    @classmethod
    def get_stack_features(cls, stack_name: str) -> List[str]:
        """Get feature list for a stack."""
        requirements = cls.get_stack_requirements(stack_name)
        return requirements.get('features', [])
    
    @classmethod
    def validate_stack_config(cls, stack_name: str) -> List[str]:
        """Validate stack configuration and return any errors."""
        errors = []
        
        try:
            config = cls.load_stack_config(stack_name)
        except FileNotFoundError:
            return [f"Stack configuration file not found: {stack_name}.yml"]
        
        # Validate required fields
        required_fields = ['id', 'name', 'description', 'services']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate services exist
        if 'services' in config:
            for service in config['services']:
                service_file = cls.SERVICE_DIR / f"{service}.yml"
                if not service_file.exists():
                    # Check if service is defined in another service file
                    if not cls._service_exists_in_any_file(service):
                        errors.append(f"Service not found: {service}")
        
        # Validate ports are numbers
        requirements = config.get('requirements', {})
        ports = requirements.get('ports', [])
        for port in ports:
            if not isinstance(port, int):
                errors.append(f"Invalid port number: {port}")
        
        # Validate access URL format
        access_url = config.get('access_url', '')
        if access_url and not (access_url.startswith('http://') or access_url.startswith('https://')):
            errors.append(f"Invalid access URL format: {access_url}")
        
        return errors
    
    @classmethod
    def get_all_stacks(cls) -> List[Dict]:
        """Get metadata for all available stacks."""
        stacks = []
        for stack_file in cls.STACK_DIR.glob("*.yml"):
            try:
                config = cls.load_stack_config(stack_file.stem)
                stacks.append({
                    'id': config.get('id', stack_file.stem),
                    'name': config.get('name', stack_file.stem.title()),
                    'description': config.get('description', ''),
                    'access_url': config.get('access_url', ''),
                    'requirements': config.get('requirements', {}),
                    'services': config.get('services', [])
                })
            except Exception:
                # Skip invalid stack files
                continue
        
        return sorted(stacks, key=lambda x: x['id'])
    
    @classmethod
    def stack_exists(cls, stack_name: str) -> bool:
        """Check if a stack configuration file exists."""
        stack_file = cls.STACK_DIR / f"{stack_name}.yml"
        return stack_file.exists()
    
    @classmethod
    def get_stack_ports(cls, stack_name: str) -> List[int]:
        """Get list of ports used by a stack."""
        requirements = cls.get_stack_requirements(stack_name)
        return requirements.get('ports', [])
    
    @classmethod
    def get_monitoring_urls(cls, stack_name: str) -> Dict[str, str]:
        """Get monitoring service URLs if stack includes monitoring."""
        urls = {}
        services = cls.get_stack_services(stack_name)
        
        # Define monitoring service URLs
        monitoring_services = {
            'grafana': 'http://localhost:3000',
            'prometheus': 'http://localhost:9090',
            'kibana': 'http://localhost:5601',
            'jaeger': 'http://localhost:16686'
        }
        
        for service in services:
            if service in monitoring_services:
                urls[service] = monitoring_services[service]
        
        return urls
    
    @classmethod
    def _service_exists_in_any_file(cls, service_name: str) -> bool:
        """Check if a service is defined in any service file."""
        for yml_file in cls.SERVICE_DIR.glob("*.yml"):
            try:
                with open(yml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'services' in data and service_name in data['services']:
                        return True
            except Exception:
                continue
        return False
    
    @classmethod
    def get_stack_info(cls, stack_name: str) -> Dict:
        """Get complete stack information including validation."""
        try:
            config = cls.load_stack_config(stack_name)
            errors = cls.validate_stack_config(stack_name)
            
            return {
                'id': config.get('id', stack_name),
                'name': config.get('name', stack_name.title()),
                'description': config.get('description', ''),
                'access_url': config.get('access_url', ''),
                'requirements': config.get('requirements', {}),
                'services': config.get('services', []),
                'monitoring_urls': cls.get_monitoring_urls(stack_name),
                'valid': len(errors) == 0,
                'errors': errors
            }
        except FileNotFoundError:
            return {
                'id': stack_name,
                'name': stack_name.title(),
                'description': 'Stack not found',
                'valid': False,
                'errors': [f"Stack configuration not found: {stack_name}"]
            }