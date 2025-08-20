#!/usr/bin/env python3
"""Tests for service discovery functionality."""

import unittest
import tempfile
import os
from pathlib import Path
import yaml
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app.service_discovery import ServiceDiscovery


class TestServiceDiscovery(unittest.TestCase):
    """Test cases for ServiceDiscovery class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.services_dir = Path(self.test_dir) / 'docker' / 'services'
        self.services_dir.mkdir(parents=True)
        
        # Create sample service files
        self.create_test_service('php-fpm', 'php', ['web', 'cli'], 'PHP-FPM processor')
        self.create_test_service('mysql', 'database', ['storage', 'primary'], 'MySQL database')
        self.create_test_service('redis', 'cache', ['cache', 'session', 'queue'], 'Redis server')
        self.create_test_service('nginx', 'proxy', ['web'], 'Nginx reverse proxy')
        
        # Store original values
        self.original_project_root = os.environ.get('PROJECT_ROOT')
        
        # Set PROJECT_ROOT environment variable for tests
        os.environ['PROJECT_ROOT'] = self.test_dir
        
        # Update class variables to use test directory
        ServiceDiscovery.PROJECT_ROOT = Path(self.test_dir)
        ServiceDiscovery.SERVICE_DIR = Path(self.test_dir) / "docker" / "services"
        
        # Clear any caches
        ServiceDiscovery._load_service_file.cache_clear()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
        
        # Restore original PROJECT_ROOT
        if self.original_project_root is not None:
            os.environ['PROJECT_ROOT'] = self.original_project_root
        elif 'PROJECT_ROOT' in os.environ:
            del os.environ['PROJECT_ROOT']
        
        # Restore class variables
        ServiceDiscovery.PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
        ServiceDiscovery.SERVICE_DIR = ServiceDiscovery.PROJECT_ROOT / "docker" / "services"
        
        # Clear any caches
        ServiceDiscovery._load_service_file.cache_clear()
    
    def create_test_service(self, name, service_type, roles, description):
        """Create a test service file."""
        service_file = self.services_dir / f'{name}.yml'
        service_data = {
            'services': {
                name: {
                    'image': f'test/{name}:latest',
                    'labels': [
                        f'com.customer-dashboard.service.type={service_type}',
                        f'com.customer-dashboard.service.roles={",".join(roles)}',
                        f'com.customer-dashboard.service.description={description}'
                    ]
                }
            }
        }
        
        with open(service_file, 'w') as f:
            yaml.dump(service_data, f)
    
    def test_find_services_by_type(self):
        """Test finding services by type."""
        php_services = ServiceDiscovery.find_services_by_type('php')
        self.assertEqual(len(php_services), 1)
        self.assertEqual(php_services[0]['name'], 'php-fpm')
        
        cache_services = ServiceDiscovery.find_services_by_type('cache')
        self.assertEqual(len(cache_services), 1)
        self.assertEqual(cache_services[0]['name'], 'redis')
        
        # Test non-existent type
        missing_services = ServiceDiscovery.find_services_by_type('nonexistent')
        self.assertEqual(len(missing_services), 0)
    
    def test_find_services_by_role(self):
        """Test finding services by role."""
        web_services = ServiceDiscovery.find_services_by_role('web')
        web_names = [service['name'] for service in web_services]
        self.assertIn('php-fpm', web_names)
        self.assertIn('nginx', web_names)
        self.assertEqual(len(web_services), 2)
        
        storage_services = ServiceDiscovery.find_services_by_role('storage')
        self.assertEqual(len(storage_services), 1)
        self.assertEqual(storage_services[0]['name'], 'mysql')
        
        # Test role that appears in multiple services
        queue_services = ServiceDiscovery.find_services_by_role('queue')
        self.assertEqual(len(queue_services), 1)
        self.assertEqual(queue_services[0]['name'], 'redis')
    
    def test_get_service_metadata(self):
        """Test getting service metadata."""
        metadata = ServiceDiscovery.get_service_metadata('php-fpm')
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['type'], 'php')
        self.assertEqual(set(metadata['roles']), {'web', 'cli'})
        self.assertEqual(metadata['description'], 'PHP-FPM processor')
        
        # Test non-existent service
        missing_metadata = ServiceDiscovery.get_service_metadata('nonexistent')
        self.assertIsNone(missing_metadata)
    
    def test_parse_csv_roles(self):
        """Test parsing CSV role strings."""
        roles = ServiceDiscovery.parse_csv_roles('web,cli,queue')
        self.assertEqual(roles, ['web', 'cli', 'queue'])
        
        roles = ServiceDiscovery.parse_csv_roles('single')
        self.assertEqual(roles, ['single'])
        
        roles = ServiceDiscovery.parse_csv_roles('')
        self.assertEqual(roles, [])
        
        # Test with spaces (should be stripped)
        roles = ServiceDiscovery.parse_csv_roles('web, cli, queue')
        self.assertEqual(roles, ['web', 'cli', 'queue'])


if __name__ == '__main__':
    unittest.main()