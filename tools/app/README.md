# CLI Tool

A comprehensive development environment orchestrator for the customer dashboard project.

## Features

- **Intelligent Service Discovery**: Automatic container detection using Docker labels
- **Stack State Tracking**: Persistent tracking of active stacks in `.docker-state.json`
- **Branch Management**: Registry-based branch management with automatic stack switching
- **Queue Management**: Integrated Laravel queue and cache management
- **Port Conflict Detection**: Automatic detection and prevention of port conflicts
- **Rich Status Reporting**: Comprehensive environment status with uptime and access URLs

## Architecture

The tool is organized into several key modules:

- **service_discovery.py**: Docker label-based service discovery
- **stack_config.py**: Stack configuration management with metadata
- **state_manager.py**: Persistent state tracking and management
- **branch_manager.py**: Branch registry and management
- **dev_commands.py**: Daily development workflow commands
- **setup_commands.py**: Environment setup and maintenance
- **stack_commands.py**: Stack lifecycle management
- **container_commands.py**: Individual container operations

## Testing

Run the test suite:

```bash
cd tools/app
python tests/run_tests.py
```

Or run individual test files:

```bash
python -m unittest tests.test_service_discovery
python -m unittest tests.test_stack_config
python -m unittest tests.test_state_manager
python -m unittest tests.test_branch_manager
```

## Development

The tool follows a modular architecture with clear separation of concerns:

1. **Utility Classes**: Provide core functionality (discovery, config, state)
2. **Command Groups**: Organize related commands (dev, setup, stack, container)
3. **Integration Layer**: Tie components together with shared state and error handling

All components use intelligent caching for performance and graceful error handling for reliability.