# Stack Management Guide

The Laravel Performance Testing Environment uses a custom `stack.sh` script to manage different container combinations (
stacks) for various testing scenarios.

## Available Stack Configurations

### Production-Ready Stacks

#### traditional

**Components**: `base` + `traditional`  
**Containers**: MySQL, Redis, Prometheus, Grafana, Nginx, PHP-FPM  
**Purpose**: Most common production setup  
**Ports**: 80 (HTTP), 443 (HTTPS), 3306 (MySQL), 6379 (Redis)

```bash
stack up traditional -d
```

#### frankenphp

**Components**: `base` + `frankenphp`  
**Containers**: MySQL, Redis, Prometheus, Grafana, FrankenPHP  
**Purpose**: Modern HTTP/3 server with worker mode  
**Ports**: 8080 (HTTP), 8443 (HTTPS/HTTP3), 3306 (MySQL), 6379 (Redis)

```bash
stack up frankenphp -d
```

#### octane

**Components**: `base` + `octane`  
**Containers**: MySQL, Redis, Prometheus, Grafana, Laravel Octane  
**Purpose**: High-performance long-running processes  
**Ports**: 8000 (HTTP), 3306 (MySQL), 6379 (Redis)

```bash
stack up octane -d
```

### Testing & Analysis Stacks

#### performance

**Components**: `base` + `traditional` + `monitoring`  
**Containers**: Traditional stack + ELK, Jaeger, Exporters  
**Purpose**: Performance testing with comprehensive monitoring  
**Additional Ports**: 5601 (Kibana), 9200 (Elasticsearch), 16686 (Jaeger)

```bash
stack up performance -d
```

#### enterprise

**Components**: `base` + `traditional` + `monitoring` + `multitenant` + `database-tools`  
**Containers**: Full enterprise stack with multi-tenancy and database tools  
**Purpose**: Enterprise features and comprehensive analysis  
**Additional Ports**: 3307-3308 (Tenant DBs), 7010-7012 (Redis Cluster), 8090 (Load Balancer)

```bash
stack up enterprise -d
```

#### comparison

**Components**: `base` + `traditional` + `frankenphp` + `octane` + `monitoring`  
**Containers**: All web servers plus monitoring  
**Purpose**: Benchmarking different server configurations  
**Ports**: 80 (Nginx), 8080 (FrankenPHP), 8000 (Octane), plus monitoring

```bash
stack up comparison -d
```

#### full

**Components**: All components enabled  
**Containers**: Everything (25+ containers)  
**Purpose**: Complete testing environment  
**Requirements**: Minimum 8GB RAM, significant CPU resources

```bash
stack up full -d
```

#### minimal

**Components**: `base` + `traditional`  
**Containers**: Just MySQL, Redis, Nginx, PHP-FPM  
**Purpose**: Minimal setup for basic development

```bash
stack up minimal -d
```

## Stack Management Commands

### Validation

```bash
# Validate configuration files for a stack
stack validate traditional
stack validate enterprise
```

### Stack Operations

```bash
# Start a stack in background mode
stack up [STACK] -d

# Start a stack in foreground (see logs)  
stack up [STACK]

# Stop a specific stack
stack down [STACK]

# Restart a stack
stack restart [STACK]

# Force rebuild containers
stack up [STACK] -d --build

# Recreate containers
stack up [STACK] -d --recreate

# View logs for a stack
stack logs [STACK]

# Follow logs in real-time
stack logs [STACK] -f
```

### System Management

```bash
# Show status of all containers
stack status

# Stop all project containers (any stack)
stack stop-all

# Remove all containers, networks, and volumes
stack clean

# List available stacks
stack list

# Show help
stack help
```

## Stack Component Details

### Base Components (`docker-compose.yml`)

- **mysql**: Primary database server
- **redis**: Primary cache server
- **prometheus**: Metrics collection
- **grafana**: Monitoring dashboards

### Traditional Components (`docker-compose.traditional.yml`)

- **nginx**: Web server
- **php-fpm**: PHP application server

### FrankenPHP Components (`docker-compose.frankenphp.yml`)

- **frankenphp**: Modern PHP server with HTTP/3

### Octane Components (`docker-compose.octane.yml`)

- **octane**: Laravel Octane with Swoole

### Monitoring Components (`docker-compose.monitoring.yml`)

- **elasticsearch**: Log aggregation
- **kibana**: ELK dashboard
- **statsd**: Custom metrics
- **mysql-exporter**: Database metrics
- **redis-exporter**: Cache metrics
- **jaeger**: Distributed tracing

### Multi-tenant Components (`docker-compose.multitenant.yml`)

- **mysql-tenant-1/2**: Tenant databases
- **redis-cluster-1/2/3**: Redis cluster
- **nginx-lb**: Load balancer

### Database Tools (`docker-compose.database-tools.yml`)

- **percona-toolkit**: MySQL analysis
- **pt-query-digest**: Query analysis
- **proxysql**: Database proxy
- **pgbouncer**: Connection pooling

## Advanced Usage

### Custom Flags

```bash
# Detached mode (background)
stack up traditional -d

# Force rebuild images
stack up traditional -b

# Recreate containers
stack up traditional -r

# Verbose output  
stack up traditional -v

# Skip dependent services
stack up traditional --no-deps
```

### Environment Variables

The stack script respects these environment variables:

```bash
# Docker Compose project name (default: laravel-perf)
export PROJECT_NAME="my-project"

# Enable verbose output
export VERBOSE=true
```

### File Requirements

Each stack validates required configuration files:

**Traditional/Enterprise/Full stacks require:**

- `docker/nginx/nginx.conf`
- `docker/nginx/conf.d/laravel.conf`

**FrankenPHP stacks require:**

- `docker/frankenphp/Caddyfile`

**Monitoring stacks require:**

- `docker/prometheus/prometheus.yml`
- `docker/grafana/datasources/datasources.yml`

## Port Allocation Strategy

To prevent conflicts, ports are allocated as follows:

### Web Services

- **80**: Nginx (traditional stack)
- **8080**: FrankenPHP
- **8000**: Laravel Octane
- **8090**: Load balancer
- **8443**: FrankenPHP HTTPS/HTTP3

### Databases

- **3306**: Primary MySQL
- **3307**: Tenant 1 MySQL
- **3308**: Tenant 2 MySQL
- **6379**: Primary Redis
- **7010-7012**: Redis cluster nodes

### Database Tools

- **6032-6033**: ProxySQL
- **6432**: PgBouncer

### Monitoring

- **3000**: Grafana
- **9090**: Prometheus
- **9200**: Elasticsearch
- **5601**: Kibana
- **16686**: Jaeger UI
- **9104**: MySQL exporter
- **9121**: Redis exporter
- **9102**: StatsD exporter

## Resource Requirements

### Minimal Stack

- **RAM**: 2GB minimum
- **CPU**: 2 cores
- **Disk**: 5GB

### Traditional/FrankenPHP/Octane Stacks

- **RAM**: 4GB minimum
- **CPU**: 4 cores
- **Disk**: 10GB

### Performance/Comparison Stacks

- **RAM**: 6GB minimum
- **CPU**: 6 cores
- **Disk**: 15GB

### Enterprise/Full Stacks

- **RAM**: 8GB minimum (12GB recommended)
- **CPU**: 8 cores (12 cores recommended)
- **Disk**: 20GB

## Health Checks

The stack script includes built-in health monitoring:

```bash
# Check if containers are responding
curl http://localhost/health        # Nginx
curl http://localhost:8080/health   # FrankenPHP  
curl http://localhost:8090/health   # Load balancer

# Check monitoring services
curl http://localhost:3000/api/health    # Grafana
curl http://localhost:9090/-/healthy     # Prometheus
curl http://localhost:9200/_cluster/health  # Elasticsearch
```

## Troubleshooting

### Common Issues

**Port conflicts:**

```bash
# Check what's using a port
lsof -i :80
lsof -i :3306

# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop mysql
```

**Memory issues:**

```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory (8GB+)

# Check container resource usage  
docker stats
```

**Permission issues:**

```bash
# Fix storage permissions (if using Laravel)
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache
```

**Container startup failures:**

```bash
# Check logs for specific container
docker logs laravel-perf-mysql
docker logs laravel-perf-nginx

# Restart failed containers
stack restart traditional
```

For more troubleshooting information, see the [troubleshooting guide](troubleshooting.md).