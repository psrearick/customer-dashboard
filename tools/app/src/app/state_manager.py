import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os


class StateManager:
    """Persistent state tracking for Docker stacks and containers."""

    PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
    STATE_FILE = PROJECT_ROOT / ".docker-state.json"
    COMPOSE_PROJECT = "customer-dashboard"

    @classmethod
    def get_active_stacks(cls) -> Dict[str, Dict]:
        """Get all currently active stacks with verification."""
        state = cls._load_state()
        active_stacks = state.get('active_stacks', {})

        # Verify and clean up stale entries
        verified_stacks = {}
        for stack_name, stack_info in active_stacks.items():
            if cls.verify_stack_running(stack_name):
                verified_stacks[stack_name] = stack_info

        # Update state if any were removed
        if len(verified_stacks) != len(active_stacks):
            state['active_stacks'] = verified_stacks
            cls._save_state(state)

        return verified_stacks

    @classmethod
    def mark_stack_active(cls, stack_name: str, services: List[str]) -> None:
        """Mark a stack as active and record startup information."""
        from .stack_config import StackConfig

        state = cls._load_state()

        # Get stack configuration
        try:
            access_url = StackConfig.get_stack_access_url(stack_name)
            requirements = StackConfig.get_stack_requirements(stack_name)
            monitoring_urls = StackConfig.get_monitoring_urls(stack_name)
            ports = StackConfig.get_stack_ports(stack_name)
        except Exception:
            access_url = "http://localhost"
            requirements = {}
            monitoring_urls = {}
            ports = []

        # Generate container names
        container_names = cls._get_container_names_for_stack(stack_name, services)

        # Record stack information
        state['active_stacks'][stack_name] = {
            'started_at': datetime.now().isoformat(),
            'explicitly_started': True,  # This stack was intentionally started by user
            'services': services,
            'access_url': access_url,
            'monitoring_urls': monitoring_urls,
            'ports': ports,
            'stack_config': {
                'min_memory': requirements.get('min_memory', '2GB'),
                'features': requirements.get('features', [])
            },
            'containers': container_names
        }

        cls._save_state(state)

    @classmethod
    def mark_stack_inactive(cls, stack_name: str) -> None:
        """Mark a stack as inactive and remove from state."""
        state = cls._load_state()

        if stack_name in state.get('active_stacks', {}):
            del state['active_stacks'][stack_name]
            cls._save_state(state)

    @classmethod
    def verify_stack_running(cls, stack_name: str) -> bool:
        """Verify that a stack's containers are actually running."""
        stack_info = cls.get_stack_info(stack_name)
        if not stack_info:
            return False

        containers = stack_info.get('containers', {})
        explicitly_started = stack_info.get('explicitly_started', True)

        if len(containers) == 0:
            return False

        if explicitly_started:
            for container_name, status in containers.items():
                if cls._verify_container_running(container_name):
                    return True
            return False

        for container_name, status in containers.items():
            if not cls._verify_container_running(container_name):
                return False

        return True

    @classmethod
    def cleanup_stale_state(cls) -> int:
        """Remove entries for stacks that are no longer running."""
        state = cls._load_state()
        active_stacks = state.get('active_stacks', {})
        stale_count = 0

        stacks_to_remove = []
        for stack_name in active_stacks:
            if not cls.verify_stack_running(stack_name):
                stacks_to_remove.append(stack_name)
                stale_count += 1

        for stack_name in stacks_to_remove:
            del active_stacks[stack_name]

        if stale_count > 0:
            cls._save_state(state)

        return stale_count

    @classmethod
    def get_stack_uptime_seconds(cls, stack_name: str) -> int:
        stack_info = cls.get_stack_info(stack_name)
        if not stack_info:
            return 0

        started_at_str = stack_info.get('started_at')
        if not started_at_str:
            return 0

        try:
            started_at = datetime.fromisoformat(started_at_str)
            uptime = datetime.now() - started_at

            return int(uptime.total_seconds())
        except (ValueError, TypeError):
            return -1

    @classmethod
    def get_stack_uptime(cls, stack_name: str) -> str:
        """Get formatted uptime string for a specific stack."""

        total_seconds = cls.get_stack_uptime_seconds(stack_name)

        if total_seconds == 0:
            return "Not running"

        if total_seconds < 0:
            return "Unknown"

        if total_seconds < 60:
            return f"{total_seconds} seconds"

        if total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minutes"

        if total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}d {hours}h"

    @classmethod
    def get_stack_info(cls, stack_name: str) -> Optional[Dict]:
        """Get complete information for a specific stack."""
        state = cls._load_state()
        return state.get('active_stacks', {}).get(stack_name)

    @classmethod
    def update_container_status(cls, stack_name: str) -> None:
        """Update container status information for a stack."""
        stack_info = cls.get_stack_info(stack_name)
        if not stack_info:
            return

        state = cls._load_state()
        containers = stack_info.get('containers', {})

        # Update status for each container
        for container_name in containers:
            containers[container_name] = 'running' if cls._verify_container_running(container_name) else 'stopped'

        state['active_stacks'][stack_name]['containers'] = containers
        cls._save_state(state)

    @classmethod
    def get_all_ports_in_use(cls) -> List[int]:
        """Get list of all ports currently in use by active stacks."""
        ports = set()
        active_stacks = cls.get_active_stacks()

        for stack_info in active_stacks.values():
            stack_ports = stack_info.get('ports', [])
            ports.update(stack_ports)

        return sorted(list(ports))

    @classmethod
    def check_port_conflicts(cls, stack_name: str) -> List[int]:
        """Check if starting a stack would cause port conflicts."""
        from .stack_config import StackConfig

        # Get ports needed by the stack
        try:
            needed_ports = StackConfig.get_stack_ports(stack_name)
        except Exception:
            return []

        # Get ports currently in use
        used_ports = cls.get_all_ports_in_use()

        # Find conflicts
        conflicts = [port for port in needed_ports if port in used_ports]

        # Exclude ports used by the same stack (if restarting)
        stack_info = cls.get_stack_info(stack_name)
        if stack_info:
            stack_ports = stack_info.get('ports', [])
            conflicts = [port for port in conflicts if port not in stack_ports]

        return conflicts

    @classmethod
    def get_stack_access_info(cls, stack_name: str) -> Dict[str, str]:
        """Get access URLs and connection info for a stack."""
        stack_info = cls.get_stack_info(stack_name)
        if not stack_info:
            return {}

        access_info = {
            'main': stack_info.get('access_url', 'http://localhost')
        }

        # Add monitoring URLs
        monitoring_urls = stack_info.get('monitoring_urls', {})
        access_info.update(monitoring_urls)

        return access_info

    @classmethod
    def _load_state(cls) -> Dict:
        """Load state from file, handle missing/corrupt files."""
        if not cls.STATE_FILE.exists():
            return cls._create_empty_state()

        try:
            with open(cls.STATE_FILE, 'r') as f:
                state = json.load(f)
                # Ensure required keys exist
                if 'version' not in state:
                    state['version'] = '1.0'
                if 'active_stacks' not in state:
                    state['active_stacks'] = {}
                if 'metadata' not in state:
                    state['metadata'] = {}
                return state
        except (json.JSONDecodeError, IOError):
            # Backup corrupt file and create new one
            if cls.STATE_FILE.exists():
                backup_file = cls.STATE_FILE.with_suffix('.json.backup')
                cls.STATE_FILE.rename(backup_file)
            return cls._create_empty_state()

    @classmethod
    def _save_state(cls, state: Dict) -> None:
        """Save state to file with proper error handling."""
        state['last_updated'] = datetime.now().isoformat()
        state['metadata']['project_root'] = str(cls.PROJECT_ROOT)
        state['metadata']['docker_compose_project'] = cls.COMPOSE_PROJECT

        try:
            # Write to temporary file first
            temp_file = cls.STATE_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)

            # Atomic rename
            temp_file.replace(cls.STATE_FILE)

            # Set proper permissions (user read/write only)
            os.chmod(cls.STATE_FILE, 0o600)
        except IOError as e:
            print(f"Warning: Could not save state: {e}")

    @classmethod
    def _create_empty_state(cls) -> Dict:
        """Create new empty state structure."""
        return {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'active_stacks': {},
            'metadata': {
                'project_root': str(cls.PROJECT_ROOT),
                'docker_compose_project': cls.COMPOSE_PROJECT
            }
        }

    @classmethod
    def _verify_container_running(cls, container_name: str) -> bool:
        """Check if specific container is running."""
        try:
            result = subprocess.run(
                ['docker', 'inspect', '-f', '{{.State.Running}}', container_name],
                capture_output=True,
                text=True
            )

            return result.returncode == 0 and result.stdout.strip() == 'true'
        except subprocess.CalledProcessError:
            return False

    @classmethod
    def _get_container_names_for_stack(cls, stack_name: str, services: List[str]) -> Dict[str, str]:
        """Generate container names from service list."""
        containers = {}
        for service in services:
            container_name = f"{cls.COMPOSE_PROJECT}-{service}"
            status = 'running' if cls._verify_container_running(container_name) else 'stopped'
            containers[container_name] = status
        return containers

    @classmethod
    def _collect_monitoring_urls(cls, services: List[str]) -> Dict[str, str]:
        """Determine monitoring URLs based on services."""
        monitoring_services = {
            'grafana': 'http://localhost:3000',
            'prometheus': 'http://localhost:9090',
            'kibana': 'http://localhost:5601',
            'jaeger': 'http://localhost:16686'
        }

        urls = {}
        for service in services:
            if service in monitoring_services:
                urls[service] = monitoring_services[service]

        return urls

    @classmethod
    def reset_state(cls) -> None:
        """Reset all state (use with caution)."""
        state = cls._create_empty_state()
        cls._save_state(state)

    @classmethod
    def rediscover_running_stacks(cls) -> int:
        """Re-discover and track any currently running stacks."""
        import subprocess

        discovered_count = 0
        try:
            # Find all running containers with our project label
            result = subprocess.run(
                [
                    'docker', 'ps', '--format', '{{json .}}',
                    '--filter', f'label=com.docker.compose.project={cls.COMPOSE_PROJECT}'
                ],
                capture_output=True,
                text=True,
                check=True
            )

            # Get all running services
            services_running = set()
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container_data = json.loads(line)
                        labels = container_data.get('Labels', '')

                        # Extract service name from labels
                        for label_pair in labels.split(','):
                            if 'com.docker.compose.service=' in label_pair:
                                service_name = label_pair.split('=', 1)[1]
                                services_running.add(service_name)
                                break
                    except json.JSONDecodeError:
                        continue

            # Find the best matching stack for running services
            if services_running:
                from .stack_config import StackConfig
                all_stacks = StackConfig.get_all_stacks()

                # Find stacks that have 100% of their services running (complete matches only)
                complete_matches = []
                for stack_info in all_stacks:
                    stack_id = stack_info['id']
                    stack_services = set(stack_info['services'])

                    # Only consider stacks where ALL services are running
                    if stack_services.issubset(services_running):
                        complete_matches.append((stack_id, stack_services, len(stack_services)))

                # Sort by number of services (prefer more specific stacks)
                complete_matches.sort(key=lambda x: x[2], reverse=True)

                # Mark the most specific non-overlapping stacks as active
                used_services = set()
                for stack_id, stack_services, service_count in complete_matches:
                    # Only add if this stack doesn't overlap with already used services
                    if not stack_services.intersection(used_services):
                        # Mark as implicitly started (not explicitly by user)
                        cls._mark_stack_active_implicit(stack_id, list(stack_services))
                        used_services.update(stack_services)
                        discovered_count += 1

        except (subprocess.CalledProcessError, Exception):
            pass

        return discovered_count

    @classmethod
    def _mark_stack_active_implicit(cls, stack_name: str, services: List[str]) -> None:
        """Mark a stack as active but implicitly discovered (not explicitly started)."""
        from .stack_config import StackConfig

        state = cls._load_state()

        # Get stack configuration
        try:
            access_url = StackConfig.get_stack_access_url(stack_name)
            requirements = StackConfig.get_stack_requirements(stack_name)
            monitoring_urls = StackConfig.get_monitoring_urls(stack_name)
            ports = StackConfig.get_stack_ports(stack_name)
        except Exception:
            access_url = "http://localhost"
            requirements = {}
            monitoring_urls = {}
            ports = []

        # Generate container names
        container_names = cls._get_container_names_for_stack(stack_name, services)

        # Record stack information (marked as implicitly discovered)
        state['active_stacks'][stack_name] = {
            'started_at': datetime.now().isoformat(),
            'explicitly_started': False,  # This stack was inferred from running containers
            'services': services,
            'access_url': access_url,
            'monitoring_urls': monitoring_urls,
            'ports': ports,
            'stack_config': {
                'min_memory': requirements.get('min_memory', '2GB'),
                'features': requirements.get('features', [])
            },
            'containers': container_names
        }

        cls._save_state(state)

    @classmethod
    def get_state_summary(cls) -> Dict:
        """Get summary of current state."""
        active_stacks = cls.get_active_stacks()

        return {
            'active_stack_count': len(active_stacks),
            'active_stacks': list(active_stacks.keys()),
            'ports_in_use': cls.get_all_ports_in_use(),
            'state_file': str(cls.STATE_FILE),
            'state_file_exists': cls.STATE_FILE.exists()
        }
