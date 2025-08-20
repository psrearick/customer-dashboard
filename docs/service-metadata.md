# Service Metadata System

## Overview

The service metadata system provides intelligent service discovery through standardized Docker labels. This eliminates hardcoded container detection and enables dynamic service management.

## Label Schema

All Docker services use the `com.customer-dashboard.service.*` namespace with three core labels:

```yaml
labels:
  - "com.customer-dashboard.service.type=<service_type>"
  - "com.customer-dashboard.service.roles=<role1>,<role2>,..."
  - "com.customer-dashboard.service.description=<description>"
```

### Service Types

| Type | Description | Examples |
|------|-------------|----------|
| `php` | PHP processing containers | php-fpm, frankenphp, octane |
| `database` | Data storage services | mysql, postgresql |
| `cache` | Caching services | redis, memcached |
| `build` | Asset building tools | node, webpack |
| `monitoring` | Monitoring tools | grafana, prometheus |
| `search` | Search engines | elasticsearch, milvus |
| `proxy` | Load balancers, reverse proxies | nginx, traefik |
| `queue` | Queue processing services | redis (queue role) |

### Service Roles

| Role | Description | Use Cases |
|------|-------------|-----------|
| `web` | Handles HTTP requests | nginx, frankenphp |
| `cli` | Supports command-line operations | php-fpm, octane |
| `storage` | Data persistence | mysql, redis |
| `primary` | Primary instance of service type | mysql (main database) |
| `cache` | Caching functionality | redis (cache role) |
| `session` | Session storage | redis (session role) |
| `queue` | Queue backend | redis (queue role) |
| `assets` | Frontend asset compilation | node |
| `metrics` | Performance monitoring | prometheus, grafana |
| `logs` | Log aggregation | elasticsearch |

### Multiple Roles

Services can have multiple roles using comma-separated values:

```yaml
labels:
  - "com.customer-dashboard.service.type=cache"
  - "com.customer-dashboard.service.roles=cache,session,queue"
  - "com.customer-dashboard.service.description=Redis server for caching, sessions, and queues"
```

## Service Examples

### PHP Services

**PHP-FPM (Traditional)**:
```yaml
services:
  php-fpm:
    labels:
      - "com.customer-dashboard.service.type=php"
      - "com.customer-dashboard.service.roles=web,cli"
      - "com.customer-dashboard.service.description=PHP-FPM processor for traditional LAMP stack"
```

**Laravel Octane**:
```yaml
services:
  octane:
    labels:
      - "com.customer-dashboard.service.type=php"
      - "com.customer-dashboard.service.roles=web,cli,queue"
      - "com.customer-dashboard.service.description=Laravel Octane with Swoole for high performance"
```

**FrankenPHP**:
```yaml
services:
  frankenphp:
    labels:
      - "com.customer-dashboard.service.type=php"
      - "com.customer-dashboard.service.roles=web,cli"
      - "com.customer-dashboard.service.description=Modern PHP server with HTTP/3 support"
```

### Database Services

**MySQL**:
```yaml
services:
  mysql:
    labels:
      - "com.customer-dashboard.service.type=database"
      - "com.customer-dashboard.service.roles=storage,primary"
      - "com.customer-dashboard.service.description=Primary MySQL database server"
```

### Cache Services

**Redis**:
```yaml
services:
  redis:
    labels:
      - "com.customer-dashboard.service.type=cache"
      - "com.customer-dashboard.service.roles=cache,session,queue"
      - "com.customer-dashboard.service.description=Redis server for caching, sessions, and queues"
```

### Build Services

**Node.js**:
```yaml
services:
  node:
    labels:
      - "com.customer-dashboard.service.type=build"
      - "com.customer-dashboard.service.roles=assets"
      - "com.customer-dashboard.service.description=Node.js for frontend asset compilation"
```

### Proxy Services

**Nginx**:
```yaml
services:
  nginx:
    labels:
      - "com.customer-dashboard.service.type=proxy"
      - "com.customer-dashboard.service.roles=web"
      - "com.customer-dashboard.service.description=Nginx reverse proxy and static file server"
```

### Monitoring Services

**Grafana**:
```yaml
services:
  grafana:
    labels:
      - "com.customer-dashboard.service.type=monitoring"
      - "com.customer-dashboard.service.roles=metrics"
      - "com.customer-dashboard.service.description=Grafana dashboards for performance monitoring"
```

**Prometheus**:
```yaml
services:
  prometheus:
    labels:
      - "com.customer-dashboard.service.type=monitoring"
      - "com.customer-dashboard.service.roles=metrics"
      - "com.customer-dashboard.service.description=Prometheus metrics collection and alerting"
```

## Service Discovery API

The `ServiceDiscovery` class provides methods to query services by metadata:

### Find Services by Type

```python
from app.service_discovery import ServiceDiscovery

# Find all PHP services
php_services = ServiceDiscovery.find_services_by_type("php")
# Returns: [{'name': 'php-fpm', 'file_path': Path(...), 'labels': {...}}]

# Get running PHP containers
php_containers = ServiceDiscovery.get_running_containers_by_type("php")
# Returns: ['customer-dashboard-php-fpm', 'customer-dashboard-octane']
```

### Find Services by Role

```python
# Find all web-facing services
web_services = ServiceDiscovery.find_services_by_role("web")
# Returns services with 'web' in their roles

# Get running web containers
web_containers = ServiceDiscovery.get_running_containers_by_role("web")
# Returns: ['customer-dashboard-nginx', 'customer-dashboard-frankenphp']
```

### Get Specific Container Types

```python
# Get the currently running PHP container
php_container = ServiceDiscovery.get_php_container()
# Returns: 'customer-dashboard-php-fpm' or None

# Get database container (prefers primary role)
db_container = ServiceDiscovery.get_database_container()
# Returns: 'customer-dashboard-mysql' or None

# Get cache container
cache_container = ServiceDiscovery.get_cache_container()
# Returns: 'customer-dashboard-redis' or None

# Get Node.js container
node_container = ServiceDiscovery.get_node_container()
# Returns: 'customer-dashboard-node' or None
```

### Query Docker Directly

```python
# Query running containers by label
containers = ServiceDiscovery.query_docker_labels("com.customer-dashboard.service.type=php")
# Returns: [{'name': 'customer-dashboard-octane', 'labels': {...}, 'status': 'running'}]
```

### Get Service Metadata

```python
# Get complete metadata for a service
metadata = ServiceDiscovery.get_service_metadata("octane")
# Returns: {'type': 'php', 'roles': ['web', 'cli', 'queue'], 'description': '...'}
```

## Docker Queries

You can also query services directly using Docker commands:

### Find by Type
```bash
docker ps --filter label=com.customer-dashboard.service.type=php --format "table {{.Names}}\t{{.Status}}"
```

### Find by Role
```bash
docker ps --filter label=com.customer-dashboard.service.roles=web --format json
```

### List All Services
```bash
docker ps --filter label=com.customer-dashboard.service.type --format "table {{.Names}}\t{{.Label \"com.customer-dashboard.service.type\"}}\t{{.Label \"com.customer-dashboard.service.roles\"}}"
```

## Container Naming Convention

All containers follow the naming pattern: `customer-dashboard-{service-name}`

Examples:
- `customer-dashboard-php-fpm`
- `customer-dashboard-mysql`
- `customer-dashboard-redis`
- `customer-dashboard-octane`

## Troubleshooting

### Service Not Found

If service discovery can't find expected services:

1. **Check service file exists**: Verify the service YAML file exists in `docker/services/`
2. **Verify labels**: Ensure the service file contains all required labels
3. **Check container naming**: Container names must follow the `customer-dashboard-{service}` pattern
4. **Validate Docker**: Run `docker ps` to see if containers are actually running

### Label Format Issues

Common label formatting problems:

- **Missing namespace**: Labels must start with `com.customer-dashboard.service.`
- **Invalid role CSV**: Multiple roles must be comma-separated without spaces
- **Typos in type/role**: Check against the documented types and roles above

### Container Detection Issues

If containers aren't being detected:

1. **Check container status**: `docker ps -a` to see all containers
2. **Verify labels**: `docker inspect <container> | grep com.customer-dashboard`
3. **Test queries**: Use the Docker commands above to test label queries
4. **Check naming**: Ensure containers follow the naming convention

### Performance Issues

The service discovery system includes caching for better performance:

- Service file metadata is cached with `@lru_cache`
- Docker queries are made only when needed
- File system operations are minimized

If experiencing slowness:
1. Check Docker daemon responsiveness
2. Verify file system permissions on service files
3. Consider reducing the number of running containers

## Integration Examples

### Using in Commands

```python
# In a command that needs PHP container
from app.service_discovery import ServiceDiscovery

def run_artisan_command(command):
    php_container = ServiceDiscovery.get_php_container()
    if not php_container:
        raise RuntimeError("No PHP container found. Start a stack first.")
    
    # Run command in PHP container
    subprocess.run(["docker", "exec", php_container, "php", "artisan"] + command)
```

### Stack Validation

```python
# Validate that all services in a stack exist
from app.service_discovery import ServiceDiscovery
from app.stack_config import StackConfig

def validate_stack(stack_name):
    services = StackConfig.get_stack_services(stack_name)
    for service in services:
        metadata = ServiceDiscovery.get_service_metadata(service)
        if not metadata:
            raise ValueError(f"Service '{service}' not found in stack '{stack_name}'")
```

This metadata system provides a robust foundation for intelligent container management and eliminates the need for hardcoded service detection throughout the codebase.