#!/usr/bin/env python3
"""Tests for branch management functionality."""

import unittest
import tempfile
import os
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app.branch_manager import BranchManager


class TestBranchManager(unittest.TestCase):
    """Test cases for BranchManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.branches_file = Path(self.test_dir) / 'branches.yml'
        
        self.original_project_root = os.environ.get('PROJECT_ROOT')
        
        branches_data = {
            'branches': {
                'feature/test-branch': {
                    'title': 'Test Branch',
                    'description': 'A test branch for testing',
                    'blog_post': 'https://example.com/test',
                    'stack': 'default',
                    'alternative_stacks': ['octane'],
                    'setup_commands': [
                        'artisan migrate:fresh --seed',
                        'artisan test:setup'
                    ],
                    'features': ['testing', 'demo'],
                    'requirements': {
                        'min_memory': '2GB'
                    }
                },
                'perf/performance-test': {
                    'title': 'Performance Test',
                    'description': 'Load testing examples',
                    'blog_post': 'https://example.com/performance',
                    'stack': 'octane',
                    'setup_commands': [
                        'artisan migrate:fresh --seed',
                        'artisan performance:setup'
                    ],
                    'features': ['performance', 'optimization'],
                    'requirements': {
                        'min_memory': '4GB'
                    }
                }
            }
        }
        
        with open(self.branches_file, 'w') as f:
            yaml.dump(branches_data, f)
        
        os.environ['PROJECT_ROOT'] = self.test_dir
        
        BranchManager.PROJECT_ROOT = Path(self.test_dir)
        BranchManager.REGISTRY_FILE = self.branches_file
        
        # Clear the cache
        BranchManager.load_branch_registry.cache_clear()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
        
        if self.original_project_root is not None:
            os.environ['PROJECT_ROOT'] = self.original_project_root
        elif 'PROJECT_ROOT' in os.environ:
            del os.environ['PROJECT_ROOT']
        
        BranchManager.PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
        BranchManager.REGISTRY_FILE = BranchManager.PROJECT_ROOT / "branches.yml"
        
        # Clear the cache
        BranchManager.load_branch_registry.cache_clear()
    
    def test_load_branch_registry(self):
        """Test loading branch registry."""
        registry = BranchManager.load_branch_registry()
        self.assertEqual(len(registry), 2)
        self.assertIn('feature/test-branch', registry)
        self.assertIn('perf/performance-test', registry)
    
    def test_load_branch_config(self):
        """Test loading specific branch configuration."""
        config = BranchManager.load_branch_config('feature/test-branch')
        self.assertIsNotNone(config)
        self.assertEqual(config['title'], 'Test Branch')
        self.assertEqual(config['stack'], 'default')
        self.assertEqual(config['features'], ['testing', 'demo'])
        
        # Test non-existent branch
        config = BranchManager.load_branch_config('nonexistent')
        self.assertIsNone(config)
    
    def test_get_branch_requirements(self):
        """Test getting branch requirements."""
        req = BranchManager.get_branch_requirements('feature/test-branch')
        self.assertEqual(req['stack'], 'default')
        self.assertEqual(req['min_memory'], '2GB')
        self.assertEqual(req['alternative_stacks'], ['octane'])
        
        req = BranchManager.get_branch_requirements('perf/performance-test')
        self.assertEqual(req['stack'], 'octane')
        self.assertEqual(req['min_memory'], '4GB')
    
    def test_list_available_branches(self):
        """Test listing all available branches."""
        branches = BranchManager.list_available_branches()
        self.assertEqual(len(branches), 2)
        
        branch_names = [branch['name'] for branch in branches]
        self.assertIn('feature/test-branch', branch_names)
        self.assertIn('perf/performance-test', branch_names)
        
        for branch in branches:
            self.assertIn('title', branch)
            self.assertIn('description', branch)
            self.assertIn('stack', branch)
    
    def test_get_branches_by_feature(self):
        """Test finding branches by feature."""
        testing_branches = BranchManager.get_branches_by_feature('testing')
        self.assertEqual(len(testing_branches), 1)
        self.assertEqual(testing_branches[0], 'feature/test-branch')
        
        performance_branches = BranchManager.get_branches_by_feature('performance')
        self.assertEqual(len(performance_branches), 1)
        self.assertEqual(performance_branches[0], 'perf/performance-test')
        
        demo_branches = BranchManager.get_branches_by_feature('demo')
        self.assertEqual(len(demo_branches), 1)
        self.assertIn('feature/test-branch', demo_branches)
        
        missing_branches = BranchManager.get_branches_by_feature('nonexistent')
        self.assertEqual(len(missing_branches), 0)
    
    def test_get_branch_stack_requirements(self):
        """Test getting complete stack requirements."""
        req = BranchManager.get_branch_stack_requirements('feature/test-branch')
        self.assertEqual(req['stack'], 'default')
        self.assertEqual(req['alternative_stacks'], ['octane'])
        self.assertEqual(req['additional_services'], [])
        
        req = BranchManager.get_branch_stack_requirements('perf/performance-test')
        self.assertEqual(req['stack'], 'octane')
    
    def test_get_setup_commands(self):
        """Test getting setup commands."""
        commands = BranchManager.get_setup_commands('feature/test-branch')
        expected_commands = [
            'artisan migrate:fresh --seed',
            'artisan test:setup'
        ]
        self.assertEqual(commands, expected_commands)
        
        commands = BranchManager.get_setup_commands('perf/performance-test')
        self.assertIn('artisan performance:setup', commands)
    
    def test_get_blog_post_url(self):
        """Test getting blog post URL."""
        url = BranchManager.get_blog_post_url('feature/test-branch')
        self.assertEqual(url, 'https://example.com/test')
        
        url = BranchManager.get_blog_post_url('perf/performance-test')
        self.assertEqual(url, 'https://example.com/performance')
        
        # Test non-existent branch
        url = BranchManager.get_blog_post_url('nonexistent')
        self.assertIsNone(url)
    
    def test_search_branches(self):
        """Test searching branches."""
        results = BranchManager.search_branches('A test branch')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'feature/test-branch')
        
        results = BranchManager.search_branches('Load')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'perf/performance-test')
        
        results = BranchManager.search_branches('demo')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'feature/test-branch')
        
        results = BranchManager.search_branches('nonexistent')
        self.assertEqual(len(results), 0)
    
    def test_get_branch_info(self):
        """Test getting complete branch information."""
        info = BranchManager.get_branch_info('feature/test-branch')
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'feature/test-branch')
        self.assertTrue(info['in_registry'])
        
        # Test non-existent branch
        info = BranchManager.get_branch_info('nonexistent')
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'nonexistent')
        self.assertFalse(info['in_registry'])
    
    def test_missing_branches_file(self):
        """Test handling when branches.yml doesn't exist."""
        self.branches_file.unlink()
        
        BranchManager.load_branch_registry.cache_clear()
        
        with self.assertRaises(FileNotFoundError):
            BranchManager.load_branch_registry()
        
        branches = BranchManager.list_available_branches()
        self.assertEqual(branches, [])


if __name__ == '__main__':
    unittest.main()