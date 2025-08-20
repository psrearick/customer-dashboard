#!/usr/bin/env python3
"""Tests for stack configuration functionality."""

import unittest
import tempfile
import os
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app.stack_config import StackConfig


class TestStackConfig(unittest.TestCase):
    """Test cases for StackConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.stacks_dir = Path(self.test_dir) / 'docker' / 'stacks'
        self.stacks_dir.mkdir(parents=True)
        
        self.create_test_stack('default', {
            'id': 'default',
            'name': 'Default',
            'description': 'Default development stack',
            'access_url': 'http://localhost',
            'requirements': {
                'min_memory': '2GB',
                'ports': [80, 3306, 6379],
                'features': ['traditional_lamp']
            },
            'services': ['nginx', 'php-fpm', 'mysql', 'redis']
        })
        
        self.create_test_stack('octane', {
            'id': 'octane',
            'name': 'Octane',
            'description': 'High-performance Laravel Octane stack',
            'access_url': 'http://localhost:8000',
            'requirements': {
                'min_memory': '4GB',
                'ports': [8000, 3306, 6379],
                'features': ['swoole', 'long_running_processes']
            },
            'services': ['octane', 'mysql', 'redis']
        })
        
        self.original_project_root = os.environ.get('PROJECT_ROOT')
        
        services_dir = Path(self.test_dir) / 'docker' / 'services'
        services_dir.mkdir(parents=True, exist_ok=True)
        
        for service in ['nginx', 'php-fpm', 'mysql', 'redis', 'octane']:
            service_file = services_dir / f'{service}.yml'
            service_content = {
                'services': {
                    service: {
                        'image': f'{service}:latest',
                        'labels': [f'com.customer-dashboard.service.type={service}']
                    }
                }
            }
            with open(service_file, 'w') as f:
                yaml.dump(service_content, f)
        
        os.environ['PROJECT_ROOT'] = self.test_dir
        
        StackConfig.PROJECT_ROOT = Path(self.test_dir)
        StackConfig.STACK_DIR = Path(self.test_dir) / "docker" / "stacks"
        StackConfig.SERVICE_DIR = Path(self.test_dir) / "docker" / "services"
        
        if hasattr(StackConfig, 'load_stack_config'):
            StackConfig.load_stack_config.cache_clear()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
        
        if self.original_project_root is not None:
            os.environ['PROJECT_ROOT'] = self.original_project_root
        elif 'PROJECT_ROOT' in os.environ:
            del os.environ['PROJECT_ROOT']
        
        StackConfig.PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
        StackConfig.STACK_DIR = StackConfig.PROJECT_ROOT / "docker" / "stacks"
        StackConfig.SERVICE_DIR = StackConfig.PROJECT_ROOT / "docker" / "services"
        
        if hasattr(StackConfig, 'load_stack_config'):
            StackConfig.load_stack_config.cache_clear()
    
    def create_test_stack(self, name, config):
        """Create a test stack file."""
        stack_file = self.stacks_dir / f'{name}.yml'
        with open(stack_file, 'w') as f:
            yaml.dump(config, f)
    
    def test_load_stack_config(self):
        """Test loading stack configuration."""
        config = StackConfig.load_stack_config('default')
        self.assertEqual(config['id'], 'default')
        self.assertEqual(config['name'], 'Default')
        self.assertEqual(config['access_url'], 'http://localhost')
        
        with self.assertRaises(FileNotFoundError):
            StackConfig.load_stack_config('nonexistent')
    
    def test_stack_exists(self):
        """Test checking if stack exists."""
        self.assertTrue(StackConfig.stack_exists('default'))
        self.assertTrue(StackConfig.stack_exists('octane'))
        self.assertFalse(StackConfig.stack_exists('nonexistent'))
    
    def test_get_stack_access_url(self):
        """Test getting stack access URL."""
        url = StackConfig.get_stack_access_url('default')
        self.assertEqual(url, 'http://localhost')
        
        url = StackConfig.get_stack_access_url('octane')
        self.assertEqual(url, 'http://localhost:8000')
        
        url = StackConfig.get_stack_access_url('nonexistent')
        self.assertEqual(url, 'http://localhost')
    
    def test_get_stack_requirements(self):
        """Test getting stack requirements."""
        req = StackConfig.get_stack_requirements('default')
        self.assertEqual(req['min_memory'], '2GB')
        self.assertEqual(req['ports'], [80, 3306, 6379])
        self.assertEqual(req['features'], ['traditional_lamp'])
        
        req = StackConfig.get_stack_requirements('octane')
        self.assertEqual(req['min_memory'], '4GB')
        self.assertEqual(req['ports'], [8000, 3306, 6379])
        self.assertEqual(req['features'], ['swoole', 'long_running_processes'])
    
    def test_get_stack_services(self):
        """Test getting stack services."""
        services = StackConfig.get_stack_services('default')
        self.assertEqual(services, ['nginx', 'php-fpm', 'mysql', 'redis'])
        
        services = StackConfig.get_stack_services('octane')
        self.assertEqual(services, ['octane', 'mysql', 'redis'])
    
    def test_get_stack_features(self):
        """Test getting stack features."""
        features = StackConfig.get_stack_features('default')
        self.assertEqual(features, ['traditional_lamp'])
        
        features = StackConfig.get_stack_features('octane')
        self.assertEqual(set(features), {'swoole', 'long_running_processes'})
    
    def test_get_stack_ports(self):
        """Test getting stack ports."""
        ports = StackConfig.get_stack_ports('default')
        self.assertEqual(ports, [80, 3306, 6379])
        
        ports = StackConfig.get_stack_ports('octane')
        self.assertEqual(ports, [8000, 3306, 6379])
    
    def test_get_all_stacks(self):
        """Test getting all available stacks."""
        stacks = StackConfig.get_all_stacks()
        self.assertEqual(len(stacks), 2)
        
        stack_ids = [stack['id'] for stack in stacks]
        self.assertIn('default', stack_ids)
        self.assertIn('octane', stack_ids)
    
    def test_validate_stack_config(self):
        """Test stack configuration validation."""
        errors = StackConfig.validate_stack_config('default')
        self.assertEqual(errors, [])
        
        errors = StackConfig.validate_stack_config('octane')
        self.assertEqual(errors, [])
        
        # Invalid stack should have errors
        errors = StackConfig.validate_stack_config('nonexistent')
        self.assertGreater(len(errors), 0)
    
    def test_get_monitoring_urls(self):
        """Test getting monitoring URLs."""
        urls = StackConfig.get_monitoring_urls('default')
        self.assertEqual(urls, {})
        
        urls = StackConfig.get_monitoring_urls('octane')
        self.assertEqual(urls, {})


if __name__ == '__main__':
    unittest.main()