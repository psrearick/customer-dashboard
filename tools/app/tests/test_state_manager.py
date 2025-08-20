#!/usr/bin/env python3
"""Tests for state management functionality."""

import unittest
import tempfile
import os
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app.state_manager import StateManager


class TestStateManager(unittest.TestCase):
    """Test cases for StateManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.state_file = Path(self.test_dir) / '.docker-state.json'
        
        # Store original values
        self.original_project_root = os.environ.get('PROJECT_ROOT')
        
        # Set PROJECT_ROOT environment variable for tests
        os.environ['PROJECT_ROOT'] = self.test_dir
        
        # Update class variables to use test directory
        StateManager.PROJECT_ROOT = Path(self.test_dir)
        StateManager.STATE_FILE = self.state_file
        
        # Clear any cached state
        if hasattr(StateManager, '_clear_cache'):
            StateManager._clear_cache()
        
        # Ensure clean state file
        if self.state_file.exists():
            self.state_file.unlink()
    
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
        StateManager.PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.parent.parent.parent))
        StateManager.STATE_FILE = StateManager.PROJECT_ROOT / ".docker-state.json"
        
        # Clear any cached state
        if hasattr(StateManager, '_clear_cache'):
            StateManager._clear_cache()
    
    def test_mark_stack_active(self):
        """Test marking a stack as active."""
        services = ['nginx', 'php-fpm', 'mysql']
        StateManager.mark_stack_active('default', services)
        
        # Check that state file was created
        self.assertTrue(self.state_file.exists())
        
        # Check active stacks
        active_stacks = StateManager.get_active_stacks()
        self.assertIn('default', active_stacks)
        self.assertEqual(active_stacks['default']['services'], services)
    
    def test_mark_stack_inactive(self):
        """Test marking a stack as inactive."""
        # First mark as active
        StateManager.mark_stack_active('default', ['nginx', 'php-fpm'])
        
        # Then mark as inactive
        StateManager.mark_stack_inactive('default')
        
        # Check that stack is no longer active
        active_stacks = StateManager.get_active_stacks()
        self.assertNotIn('default', active_stacks)
    
    def test_get_active_stacks_empty(self):
        """Test getting active stacks when none are active."""
        active_stacks = StateManager.get_active_stacks()
        self.assertEqual(active_stacks, {})
    
    def test_state_file_format(self):
        """Test that state file has correct format."""
        StateManager.mark_stack_active('test-stack', ['service1', 'service2'])
        
        # Read state file directly
        with open(self.state_file, 'r') as f:
            state_data = json.load(f)
        
        # Check required fields
        self.assertIn('version', state_data)
        self.assertIn('last_updated', state_data)
        self.assertIn('active_stacks', state_data)
        self.assertIn('metadata', state_data)
        
        # Check stack data
        self.assertIn('test-stack', state_data['active_stacks'])
        stack_data = state_data['active_stacks']['test-stack']
        self.assertIn('started_at', stack_data)
        self.assertIn('services', stack_data)
        self.assertEqual(stack_data['services'], ['service1', 'service2'])
    
    def test_multiple_active_stacks(self):
        """Test handling multiple active stacks."""
        # Mock verify_stack_running to always return True for tests
        original_verify = StateManager.verify_stack_running
        StateManager.verify_stack_running = lambda name: True
        
        try:
            StateManager.mark_stack_active('stack1', ['service1'])
            StateManager.mark_stack_active('stack2', ['service2'])
            
            active_stacks = StateManager.get_active_stacks()
            self.assertEqual(len(active_stacks), 2)
            self.assertIn('stack1', active_stacks)
            self.assertIn('stack2', active_stacks)
        finally:
            # Restore original method
            StateManager.verify_stack_running = original_verify
    
    def test_get_stack_uptime(self):
        """Test getting stack uptime."""
        StateManager.mark_stack_active('test-stack', ['service1'])
        
        uptime = StateManager.get_stack_uptime('test-stack')
        self.assertIsInstance(uptime, str)
        self.assertIn('second', uptime.lower())
        
        # Test non-existent stack
        uptime = StateManager.get_stack_uptime('nonexistent')
        self.assertEqual(uptime, 'Not running')
    
    def test_state_persistence(self):
        """Test that state persists across instances."""
        # Mock verify_stack_running to always return True for tests
        original_verify = StateManager.verify_stack_running
        StateManager.verify_stack_running = lambda name: True
        
        try:
            # Mark stack active
            StateManager.mark_stack_active('persistent-stack', ['service1'])
            
            # Clear cache to simulate new instance
            StateManager._clear_cache()
            
            # Check that stack is still active
            active_stacks = StateManager.get_active_stacks()
            self.assertIn('persistent-stack', active_stacks)
        finally:
            # Restore original method
            StateManager.verify_stack_running = original_verify
    
    def test_invalid_state_file_handling(self):
        """Test handling of invalid state file."""
        # Create invalid JSON file
        with open(self.state_file, 'w') as f:
            f.write('invalid json content')
        
        # Should handle gracefully and return empty state
        active_stacks = StateManager.get_active_stacks()
        self.assertEqual(active_stacks, {})
    
    def test_missing_state_file_handling(self):
        """Test handling when state file doesn't exist."""
        # Ensure state file doesn't exist
        if self.state_file.exists():
            self.state_file.unlink()
        
        # Should handle gracefully
        active_stacks = StateManager.get_active_stacks()
        self.assertEqual(active_stacks, {})


# Add a method to StateManager for testing purposes
def _clear_cache():
    """Clear internal cache for testing."""
    if hasattr(StateManager, '_cached_state'):
        delattr(StateManager, '_cached_state')

StateManager._clear_cache = staticmethod(_clear_cache)


if __name__ == '__main__':
    unittest.main()