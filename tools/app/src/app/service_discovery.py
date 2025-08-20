import subprocess
import json
import yaml
import os
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache


class ServiceDiscovery:
    """Intelligent service discovery using Docker labels and service metadata."""

    PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
    SERVICE_DIR = PROJECT_ROOT / "docker" / "services"
    LABEL_PREFIX = "com.customer-dashboard.service"
    CONTAINER_PREFIX = "customer-dashboard"

    @classmethod
    @lru_cache(maxsize=32)
    def _load_service_file(cls, file_path: Path) -> Dict:
        """Load and parse a service YAML file."""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    @classmethod
    def find_services_by_type(cls, service_type: str) -> List[Dict]:
        """Find all services of a specific type from service files."""
        services = []
        for yml_file in cls.SERVICE_DIR.glob("*.yml"):
            data = cls._load_service_file(yml_file)
            if 'services' in data:
                for service_name, service_config in data['services'].items():
                    labels = service_config.get('labels', [])
                    for label in labels:
                        if f"{cls.LABEL_PREFIX}.type={service_type}" in label:
                            services.append({
                                'name': service_name,
                                'file_path': yml_file,
                                'labels': cls._parse_labels(labels)
                            })
                            break
        return services

    @classmethod
    def find_services_by_role(cls, role: str) -> List[Dict]:
        """Find all services with a specific role from service files."""
        services = []
        for yml_file in cls.SERVICE_DIR.glob("*.yml"):
            data = cls._load_service_file(yml_file)
            if 'services' in data:
                for service_name, service_config in data['services'].items():
                    labels = service_config.get('labels', [])
                    parsed_labels = cls._parse_labels(labels)
                    roles = cls.parse_csv_roles(parsed_labels.get('roles', ''))
                    if role in roles:
                        services.append({
                            'name': service_name,
                            'file_path': yml_file,
                            'labels': parsed_labels
                        })
        return services

    @classmethod
    def get_running_containers_by_type(cls, service_type: str) -> List[str]:
        """Get running container names for a specific service type."""
        try:
            result = subprocess.run(
                [
                    'docker', 'ps',
                    '--filter', f'label={cls.LABEL_PREFIX}.type={service_type}',
                    '--format', '{{.Names}}'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        except subprocess.CalledProcessError:
            return []

    @classmethod
    def get_running_containers_by_role(cls, role: str) -> List[str]:
        """Get running container names for a specific role."""
        containers = []
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    labels = container.get('Labels', '')
                    if f'{cls.LABEL_PREFIX}.roles' in labels:
                        for label_pair in labels.split(','):
                            if f'{cls.LABEL_PREFIX}.roles=' in label_pair:
                                roles_value = label_pair.split('=', 1)[1]
                                if role in cls.parse_csv_roles(roles_value):
                                    containers.append(container['Names'])
                                break
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        return containers

    @classmethod
    def get_php_container(cls) -> Optional[str]:
        """Get the currently running PHP container name."""
        containers = cls.get_running_containers_by_type('php')
        return containers[0] if containers else None

    @classmethod
    def get_database_container(cls) -> Optional[str]:
        """Get the currently running database container name."""
        containers = cls.get_running_containers_by_type('database')
        for container in containers:
            labels = cls._get_container_labels(container)
            if 'primary' in cls.parse_csv_roles(labels.get('roles', '')):
                return container
        return containers[0] if containers else None

    @classmethod
    def get_cache_container(cls) -> Optional[str]:
        """Get the currently running cache container name."""
        containers = cls.get_running_containers_by_type('cache')
        return containers[0] if containers else None

    @classmethod
    def get_node_container(cls) -> Optional[str]:
        """Get the currently running Node.js container name."""
        containers = cls.get_running_containers_by_type('build')
        for container in containers:
            if 'node' in container.lower():
                return container
        return containers[0] if containers else None

    @classmethod
    def query_docker_labels(cls, label_filter: str) -> List[Dict]:
        """Query Docker daemon for containers with specific labels."""
        containers = []
        try:
            result = subprocess.run(
                [
                    'docker', 'ps',
                    '--filter', f'label={label_filter}',
                    '--format', '{{json .}}'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    container_data = json.loads(line)
                    containers.append({
                        'name': container_data['Names'],
                        'labels': cls._parse_label_string(container_data.get('Labels', '')),
                        'status': container_data['Status']
                    })
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        return containers

    @classmethod
    def parse_csv_roles(cls, roles_string: str) -> List[str]:
        """Parse CSV role string into list."""
        if not roles_string:
            return []
        return [role.strip() for role in roles_string.split(',')]

    @classmethod
    def get_service_metadata(cls, service_name: str) -> Optional[Dict]:
        """Get complete metadata for a service from its YAML file."""
        for yml_file in cls.SERVICE_DIR.glob("*.yml"):
            data = cls._load_service_file(yml_file)
            if 'services' in data and service_name in data['services']:
                service_config = data['services'][service_name]
                labels = cls._parse_labels(service_config.get('labels', []))
                return {
                    'type': labels.get('type'),
                    'roles': cls.parse_csv_roles(labels.get('roles', '')),
                    'description': labels.get('description', '')
                }
        return None

    @classmethod
    def _parse_labels(cls, labels: List[str]) -> Dict[str, str]:
        """Parse label list into dictionary."""
        parsed = {}
        for label in labels:
            if '=' in label:
                label = label.strip('"').strip("'")
                if label.startswith(cls.LABEL_PREFIX):
                    key_value = label[len(cls.LABEL_PREFIX) + 1:]
                    if '=' in key_value:
                        key, value = key_value.split('=', 1)
                        parsed[key] = value
        return parsed

    @classmethod
    def _parse_label_string(cls, label_string: str) -> Dict[str, str]:
        """Parse Docker label string format into dictionary."""
        parsed = {}
        for label_pair in label_string.split(','):
            if '=' in label_pair and cls.LABEL_PREFIX in label_pair:
                key_full, value = label_pair.split('=', 1)
                if '.' in key_full:
                    key = key_full.split('.')[-1]
                    parsed[key] = value
        return parsed

    @classmethod
    def _get_container_labels(cls, container_name: str) -> Dict[str, str]:
        """Get labels for a specific container."""
        try:
            result = subprocess.run(
                ['docker', 'inspect', container_name, '--format', '{{json .Config.Labels}}'],
                capture_output=True,
                text=True,
                check=True
            )
            labels = json.loads(result.stdout)
            return cls._parse_labels_dict(labels)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {}

    @classmethod
    def _parse_labels_dict(cls, labels: Dict) -> Dict[str, str]:
        """Parse Docker labels dictionary."""
        parsed = {}
        if labels:
            for key, value in labels.items():
                if key.startswith(cls.LABEL_PREFIX):
                    short_key = key[len(cls.LABEL_PREFIX) + 1:]
                    parsed[short_key] = value
        return parsed
