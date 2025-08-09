# Configuration Reference Guide

This document provides comprehensive details about all configuration files in the Laravel Performance Testing
Environment, explaining what each setting does and when you might want to modify them.

## Configuration Overview

The project includes pre-configured setups for all services. All configuration files are located in the `docker/`
directory and are organized by service type.

**Directory Structure:**

```
docker/
├── artillery/         # Load testing configurations
├── frankenphp/        # FrankenPHP web server configs
├── grafana/           # Monitoring dashboards and data sources
├── mysql/             # Database server configuration
├── nginx/             # Traditional web server configs
├── octane/            # Laravel Octane configurations
├── percona/           # Database analysis tools
├── php/               # PHP runtime configurations
├── php-fpm/           # PHP-FPM process manager
├── prometheus/        # Metrics collection configuration
├── proxysql/          # Database proxy configuration
├── redis/             # Cache server configuration
└── xhprof/            # PHP profiling tool
```

## Web Server Configurations

### Nginx Configuration

**Main Config:** `docker/nginx/nginx.conf`

```nginx
worker_processes auto;           # Automatically scale with CPU cores
keepalive_timeout 65;            # Connection timeout for clients
client_max_body_size 64M;        # Maximum upload size
```

**When to modify:**

- **worker_processes**: Set to specific number for fixed resources
- **keepalive_timeout**: Reduce for high-traffic scenarios (15-30s)
- **client_max_body_size**: Increase for larger file uploads

**Laravel Virtual Host:** `docker/nginx/conf.d/laravel.conf`

```nginx
fastcgi_buffer_size 16k;        # Initial response buffer
fastcgi_buffers 256 16k;        # Response buffering
fastcgi_busy_buffers_size 256k; # Busy buffer size
fastcgi_read_timeout 300;       # PHP script timeout
```

**Common Modifications:**

- **Increase buffer sizes** for applications with large responses
- **Adjust timeout** for long-running operations
- **Add custom headers** for specific security requirements

**Load Balancer:** `docker/nginx/load-balancer.conf`

```nginx
upstream laravel_backend {
    server nginx:80;
    keepalive 32;              # Connection pool size
}
proxy_connect_timeout 5s;      # Backend connection timeout
proxy_read_timeout 60s;        # Response timeout
```

**Tuning Tips:**

- **Increase keepalive** for high request volumes
- **Adjust timeouts** based on application response times
- **Add multiple backends** for load distribution

### FrankenPHP Configuration

**Main Config:** `docker/frankenphp/Caddyfile`

```caddy
frankenphp {
    worker /app/public/index.php    # Worker script path
    num_threads 4                   # Worker thread count
    max_wait_time 30s               # Maximum request wait time
}
```

**Performance Tuning:**

- **num_threads**: Increase for CPU-intensive applications (2x CPU cores)
- **max_wait_time**: Reduce for fast APIs, increase for heavy processing
- **worker mode**: Disable during development for code reload capability

**Security Headers:**

```caddy
header {
    Strict-Transport-Security "max-age=31536000"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "DENY"
    Content-Security-Policy "default-src 'self'"
}
```

## PHP Runtime Configuration

### Core PHP Settings

**Performance Config:** `docker/php/conf.d/performance.ini`

```ini
memory_limit = 512M              # Script memory limit
max_execution_time = 300         # Script timeout
realpath_cache_size = 4096K      # Filesystem cache size
realpath_cache_ttl = 3600        # Cache lifetime
```

**Common Adjustments:**

- **memory_limit**: Increase for data-heavy operations (1G, 2G)
- **max_execution_time**: Extend for batch processing (0 = unlimited)
- **realpath_cache_size**: Increase for applications with many files

### OPcache Configuration

**Config File:** `docker/php/conf.d/opcache.ini`

```ini
opcache.memory_consumption = 256      # OPcache memory pool
opcache.max_accelerated_files = 20000 # Maximum cached files
opcache.validate_timestamps = 1       # Check file modifications
opcache.revalidate_freq = 2           # Revalidation frequency
```

**JIT Settings (PHP 8.0+):**

```ini
opcache.jit_buffer_size = 128M       # JIT compilation memory
opcache.jit = 1255                   # JIT optimization level
```

**JIT Levels Explained:**

- `1255` - Full optimization (production)
- `1254` - No operand optimization
- `1205` - Function-level only
- `0` - Disabled

**Environment-Specific Settings:**

**Development:**

```ini
opcache.validate_timestamps = 1
opcache.revalidate_freq = 0     # Always check for changes
```

**Production:**

```ini
opcache.validate_timestamps = 0  # Never check file changes
opcache.save_comments = 0        # Strip comments for memory
```

### Xdebug Configuration

**Config File:** `docker/php/conf.d/xdebug.ini`

```ini
xdebug.mode = develop,debug,profile  # Enabled modes
xdebug.start_with_request = trigger  # Trigger-based activation
xdebug.client_host = host.docker.internal
xdebug.client_port = 9003
```

**Mode Options:**

- `develop` - Enhanced error display
- `debug` - Step debugging support
- `profile` - Performance profiling
- `trace` - Function call tracing

**Performance Impact:**

- **Disable in production** - Significant overhead
- **Use trigger mode** - Only activate when needed
- **Profile selectively** - Use query parameters to enable

## Database Configuration

### MySQL Configuration

**Main Config:** `docker/mysql/conf.d/performance.cnf`

```ini
# Connection Management
max_connections = 200            # Concurrent connection limit
max_allowed_packet = 64M         # Maximum packet size
interactive_timeout = 3600       # Interactive session timeout
wait_timeout = 3600              # Non-interactive timeout

# Buffer Pool (Primary Performance Setting)
innodb_buffer_pool_size = 1G      # Memory for data/index cache
innodb_buffer_pool_instances = 4  # Pool partitions

# Log Configuration
innodb_log_file_size = 256M      # Transaction log size
innodb_log_buffer_size = 64M     # Log write buffer
```

**Buffer Pool Sizing Guidelines:**

- **Development**: 512M - 1G
- **Production**: 70-80% of available RAM
- **Container Limits**: Leave 25% for OS and other processes

**I/O Performance:**

```ini
innodb_io_capacity = 1000        # IOPS capability
innodb_io_capacity_max = 2000    # Maximum burst IOPS
innodb_flush_method = O_DIRECT   # Bypass OS cache
```

**Adjust Based on Storage:**

- **SSD**: 2000+ IOPS capability
- **NVMe**: 10000+ IOPS capability
- **Traditional HDD**: 100-200 IOPS

**Query Performance:**

```ini
slow_query_log = 1                 # Enable slow query logging
long_query_time = 2                # Log queries > 2 seconds
log_queries_not_using_indexes = 1  # Log unindexed queries
```

### Redis Configuration

**Main Config:** `docker/redis/redis.conf`

```ini
# Memory Management
maxmemory 1gb                    # Memory limit
maxmemory-policy allkeys-lru     # Eviction policy

# Persistence
save 900 1                       # Save after 900s if ≥1 key changed
save 300 10                      # Save after 300s if ≥10 keys changed
appendonly yes                   # Enable AOF persistence
```

**Memory Policies:**

- `allkeys-lru` - Evict least recently used keys
- `allkeys-lfu` - Evict least frequently used keys
- `volatile-ttl` - Evict keys with shortest TTL
- `noeviction` - Return errors when memory full

**Performance Settings:**

```ini
io-threads 4                     # I/O thread count (Redis 6.0+)
io-threads-do-reads yes          # Enable threaded reads
tcp-keepalive 300                # Connection keepalive
```

## Monitoring Configuration

### Prometheus Configuration

**Main Config:** `docker/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s           # Default scrape frequency
  evaluation_interval: 15s       # Rule evaluation frequency

scrape_configs:
  - job_name: 'laravel-app'
    scrape_interval: 30s         # Application-specific interval
    metrics_path: '/metrics'     # Metrics endpoint
```

**Scrape Interval Guidelines:**

- **High-frequency metrics**: 5-10s (resource intensive)
- **Standard metrics**: 15-30s (balanced)
- **Low-frequency metrics**: 1-5m (batch jobs, background tasks)

**Recording Rules:** `docker/prometheus/recording_rules.yml`

```yaml
- record: laravel:request_rate_5m
  expr: rate(laravel_request_total[5m])

- record: laravel:error_rate_5m
  expr: rate(laravel_request_total{status=~"5.."}[5m])
```

**Alert Rules:** `docker/prometheus/alert_rules.yml`

```yaml
- alert: HighResponseTime
  expr: laravel:response_time_p95_5m > 1
  for: 2m
  labels:
    severity: warning
```

### Grafana Configuration

**Data Sources:** `docker/grafana/datasources/datasources.yml`

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    jsonData:
      timeInterval: "15s"        # Default time interval
      queryTimeout: "60s"        # Query timeout
```

## Service-Specific Configurations

### Laravel Octane

**Supervisor Config:** `docker/octane/supervisord.conf`

```ini
[program:octane]
command = php artisan octane:start --host=0.0.0.0 --port=8000
numprocs = 1
```

**Environment Variables:**

```bash
OCTANE_SERVER=swoole            # Server type (swoole/roadrunner)
OCTANE_WORKERS=4                # Worker processes
OCTANE_TASK_WORKERS=6           # Background task workers
OCTANE_MAX_REQUESTS=500         # Requests per worker before restart
```

**Worker Sizing Guidelines:**

- **CPU Bound**: 1x CPU cores
- **I/O Bound**: 2x CPU cores
- **Mixed Workload**: 1.5x CPU cores

### ProxySQL Configuration

**Main Config:** `docker/proxysql/proxysql.cnf`

```ini
mysql_variables = {
                  threads=4                        # MySQL thread count
                  max_connections=2048             # Connection pool size
                  default_query_timeout=36000000   # Query timeout
}

mysql_servers = (
                {
                address="mysql"
                port=3306
                hostgroup=0
                weight=900               # Load balancing weight
                max_replication_lag=10   # Replication lag threshold
                }
)
```

## Environment-Specific Customizations

### Development Environment

**PHP Settings:**

```ini
opcache.validate_timestamps = 1  # Enable file change detection
xdebug.mode = develop,debug      # Enable debugging
```

**MySQL Settings:**

```ini
innodb_buffer_pool_size = 256M   # Smaller memory footprint
slow_query_log = 1               # Enable for debugging
```

### Staging Environment

**PHP Settings:**

```ini
opcache.validate_timestamps = 1  # Periodic validation
opcache.revalidate_freq = 2      # Check every 2 seconds
```

**Monitoring:**

```yaml
scrape_interval: 15s             # Standard monitoring frequency
```

### Production Environment

**PHP Settings:**

```ini
opcache.validate_timestamps = 0  # Disable file checks
opcache.save_comments = 0        # Optimize memory usage
xdebug.mode = off                # Disable debugging
```

**MySQL Settings:**

```ini
innodb_buffer_pool_size = 4G    # Optimized for available memory
query_cache_type = 0            # Disabled in MySQL 8.0+
```

**Security Headers:**

```nginx
add_header Strict-Transport-Security "max-age=31536000" always;
add_header X-Content-Type-Options "nosniff" always;
```

## Performance Tuning Guidelines

### High Traffic Optimization

**Nginx:**

```nginx
worker_processes 8;              # Match CPU cores
worker_connections 2048;         # Increase connection handling
keepalive_timeout 30;            # Optimize for throughput
```

**PHP-FPM:**

```ini
pm = dynamic
pm.max_children = 50            # Maximum workers
pm.start_servers = 10           # Initial workers
pm.min_spare_servers = 5        # Minimum idle workers
pm.max_spare_servers = 15       # Maximum idle workers
```

### Memory Optimization

**MySQL:**

```ini
innodb_buffer_pool_size = 2G    # Increase for large datasets
key_buffer_size = 256M          # MyISAM key cache
```

**Redis:**

```ini
maxmemory 2gb                   # Increase cache size
maxmemory-policy allkeys-lru    # Efficient eviction
```

### Low Latency Optimization

**FrankenPHP:**

```caddy
frankenphp {
    worker /app/public/index.php
    num_threads 8               # Increase for concurrency
}
```

**Prometheus:**

```yaml
scrape_interval: 5s             # High-frequency monitoring
```

## Configuration Validation

Use the validation command to check configurations:

```bash
# Validate specific stack configurations
./stack.sh validate traditional
./stack.sh validate performance
./stack.sh validate enterprise

# Check specific configuration files
nginx -t -c docker/nginx/nginx.conf
php --ini | grep opcache
```

## Troubleshooting Configuration Issues

### Common Problems

**Out of Memory Errors:**

- Increase `memory_limit` in PHP
- Increase `innodb_buffer_pool_size` in MySQL
- Check `maxmemory` in Redis

**Slow Performance:**

- Enable OPcache and JIT
- Tune database buffer sizes
- Optimize web server worker counts

**Connection Errors:**

- Check `max_connections` in MySQL
- Verify `worker_connections` in Nginx
- Review timeout settings across services

This configuration reference provides the foundation for optimizing your Laravel Performance Testing Environment based
on your specific needs and constraints.