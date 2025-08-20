import subprocess
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache


class BranchManager:
    """Branch registry management and git branch operations."""

    PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
    REGISTRY_FILE = PROJECT_ROOT / "branches.yml"

    @classmethod
    @lru_cache(maxsize=1)
    def load_branch_registry(cls) -> Dict:
        """Load and parse the branches.yml registry file."""
        if not cls.REGISTRY_FILE.exists():
            raise FileNotFoundError(f"Branch registry not found at {cls.REGISTRY_FILE}")

        with open(cls.REGISTRY_FILE, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('branches', {})

    @classmethod
    def load_branch_config(cls, branch_name: str) -> Optional[Dict]:
        """Get configuration for a specific branch."""
        try:
            registry = cls.load_branch_registry()
            return registry.get(branch_name)
        except FileNotFoundError:
            return None

    @classmethod
    def get_branch_requirements(cls, branch_name: str) -> Dict:
        """Get resource requirements for a branch."""
        config = cls.load_branch_config(branch_name)
        if not config:
            return {}

        return {
            'stack': config.get('stack', 'default'),
            'min_memory': config.get('requirements', {}).get('min_memory', '2GB'),
            'additional_services': config.get('additional_services', []),
            'alternative_stacks': config.get('alternative_stacks', [])
        }

    @classmethod
    def validate_branch_exists(cls, branch_name: str) -> bool:
        """Check if branch exists in git repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--verify', f'refs/heads/{branch_name}'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ['git', 'rev-parse', '--verify', f'refs/remotes/origin/{branch_name}'],
                    capture_output=True,
                    text=True
                )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    @classmethod
    def get_current_branch(cls) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            branch = result.stdout.strip()
            return branch if branch != 'HEAD' else 'main'
        except (subprocess.CalledProcessError, FileNotFoundError):
            return 'main'

    @classmethod
    def list_available_branches(cls) -> List[Dict]:
        """Get list of all registered branches with metadata."""
        branches = []
        try:
            registry = cls.load_branch_registry()
            for branch_name, config in registry.items():
                branches.append({
                    'name': branch_name,
                    'title': config.get('title', ''),
                    'description': config.get('description', ''),
                    'stack': config.get('stack', 'default'),
                    'features': config.get('features', []),
                    'blog_post': config.get('blog_post', '')
                })
        except FileNotFoundError:
            pass

        return sorted(branches, key=lambda x: x['name'])

    @classmethod
    def get_branches_by_feature(cls, feature: str) -> List[str]:
        """Find branches that have a specific feature tag."""
        branches = []
        try:
            registry = cls.load_branch_registry()
            for branch_name, config in registry.items():
                features = config.get('features', [])
                if feature in features:
                    branches.append(branch_name)
        except FileNotFoundError:
            pass

        return sorted(branches)

    @classmethod
    def get_branch_stack_requirements(cls, branch_name: str) -> Dict:
        """Get complete stack requirements for a branch."""
        config = cls.load_branch_config(branch_name)
        if not config:
            return {
                'stack': 'default',
                'alternative_stacks': [],
                'additional_services': []
            }

        return {
            'stack': config.get('stack', 'default'),
            'alternative_stacks': config.get('alternative_stacks', []),
            'additional_services': config.get('additional_services', [])
        }

    @classmethod
    def validate_branch_config(cls, branch_name: str) -> List[str]:
        """Validate branch configuration."""
        errors = []
        config = cls.load_branch_config(branch_name)

        if not config:
            return [f"Branch '{branch_name}' not found in registry"]

        required_fields = ['title', 'description', 'stack']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        from .stack_config import StackConfig
        stack = config.get('stack')
        if stack and not StackConfig.stack_exists(stack):
            errors.append(f"Referenced stack does not exist: {stack}")

        for alt_stack in config.get('alternative_stacks', []):
            if not StackConfig.stack_exists(alt_stack):
                errors.append(f"Alternative stack does not exist: {alt_stack}")

        if not cls.validate_branch_exists(branch_name):
            errors.append(f"Git branch does not exist: {branch_name}")

        return errors

    @classmethod
    def get_setup_commands(cls, branch_name: str) -> List[str]:
        """Get setup commands for a branch."""
        config = cls.load_branch_config(branch_name)
        if not config:
            return []

        return config.get('setup_commands', [])

    @classmethod
    def search_branches(cls, query: str) -> List[Dict]:
        """Search branches by title, description, or features."""
        query_lower = query.lower()
        matches = []

        try:
            registry = cls.load_branch_registry()
            for branch_name, config in registry.items():
                if query_lower in config.get('title', '').lower():
                    matches.append({
                        'name': branch_name,
                        'config': config,
                        'match_field': 'title'
                    })
                    continue

                if query_lower in config.get('description', '').lower():
                    matches.append({
                        'name': branch_name,
                        'config': config,
                        'match_field': 'description'
                    })
                    continue

                for feature in config.get('features', []):
                    if query_lower in feature.lower():
                        matches.append({
                            'name': branch_name,
                            'config': config,
                            'match_field': 'feature'
                        })
                        break
        except FileNotFoundError:
            pass

        return matches

    @classmethod
    def get_blog_post_url(cls, branch_name: str) -> Optional[str]:
        """Get blog post URL for a branch."""
        config = cls.load_branch_config(branch_name)
        return config.get('blog_post') if config else None

    @classmethod
    def get_branch_info(cls, branch_name: str) -> Dict:
        """Get complete branch information."""
        config = cls.load_branch_config(branch_name)
        if not config:
            return {
                'name': branch_name,
                'exists': False,
                'in_registry': False
            }

        return {
            'name': branch_name,
            'exists': cls.validate_branch_exists(branch_name),
            'in_registry': True,
            'title': config.get('title', ''),
            'description': config.get('description', ''),
            'stack': config.get('stack', 'default'),
            'alternative_stacks': config.get('alternative_stacks', []),
            'additional_services': config.get('additional_services', []),
            'setup_commands': config.get('setup_commands', []),
            'features': config.get('features', []),
            'requirements': config.get('requirements', {}),
            'blog_post': config.get('blog_post', '')
        }
