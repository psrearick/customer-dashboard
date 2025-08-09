# Configuration Guide

This guide covers detailed configuration options for all services in the Laravel Performance Testing Environment.

**Note:** For comprehensive configuration details, explanations of when to modify settings, and performance tuning
guidelines, see the [Configuration Reference Guide](configuration-reference.md).

This document focuses on the actual configuration file contents and their structure.

## PHP Configuration

### Performance Settings (`docker/php/conf.d/performance.ini`)

```ini
; Memory Management
memory_limit = 512M
max_execution_time = 300
max_input_time = 300
post_max_size = 64M
upload_max_filesize = 64M

; Performance Optimization  
realpath_cache_size = 4096K
realpath_cache_ttl = 3600

; Process Control
max_input_vars = 10000
variables_order = "GPCS"
```

### OPcache Configuration (`docker/php/conf.d/opcache.ini`)

```ini
[opcache]
opcache.enable = 1
opcache.enable_cli = 1
opcache.memory_consumption = 256
opcache.interned_strings_buffer = 16
opcache.max_accelerated_files = 20000
opcache.max_wasted_percentage = 10
opcache.validate_timestamps = 1
opcache.revalidate_freq = 2
opcache.fast_shutdown = 1

; Optimization settings
opcache.optimization_level = 0x7FFFBFFF
opcache.save_comments = 0
opcache.enable_file_override = 1

; JIT compilation for PHP 8.0 and above - Enhanced for PHP 8.4
opcache.jit_buffer_size = 128M
opcache.jit = 1255
```

**JIT Configuration Options:**

- `1255` - CRTO (Call, Return, Type, Operand optimization)
- `1254` - CRT (Call, Return, Type optimization)
- `1205` - RT (Return, Type optimization)
- `0` - Disable JIT

### Xdebug Configuration (`docker/php/conf.d/xdebug.ini`)

```ini
[xdebug]
zend_extension = xdebug.so

; Profiling
xdebug.mode = develop,debug,profile
xdebug.start_with_request = trigger
xdebug.output_dir = /var/www/html/storage/logs/xdebug
xdebug.profiler_output_name = cachegrind.out.%p

; Remote Debugging  
xdebug.client_host = host.docker.internal
xdebug.client_port = 9003
xdebug.log = /var/www/html/storage/logs/xdebug/xdebug.log

; Performance
xdebug.max_nesting_level = 512
```

## Web Server Configuration

### Nginx Configuration (`docker/nginx/nginx.conf`)

```nginx
user nginx;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 64M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Include virtual hosts
    include /etc/nginx/conf.d/*.conf;
}
```

### Laravel Virtual Host (`docker/nginx/conf.d/laravel.conf`)

```nginx
server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    # Security: CVE-2019-11043 protection
    location ~ [^/]\.php(/|$) {
        fastcgi_split_path_info ^(.+?\.php)(/.*)$;
        if (!-f $document_root$fastcgi_script_name) {
            return 404;
        }
        
        fastcgi_pass php-fpm:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        
        # Performance tuning
        fastcgi_buffer_size 16k;
        fastcgi_buffers 256 16k;
        fastcgi_busy_buffers_size 256k;
        fastcgi_temp_file_write_size 256k;
        fastcgi_read_timeout 300;
    }

    # Static file caching
    location ~* \.(css|js|ico|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        log_not_found off;
    }

    # Laravel routing
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### FrankenPHP Configuration (`docker/frankenphp/Caddyfile`)

```caddy
{
    # FrankenPHP configuration
    frankenphp {
        worker /app/public/index.php
        num_threads 4
        max_wait_time 30s
    }
}

:80, :443 {
    root * /app/public

    # Compression
    encode zstd gzip

    # HTTP/3 support
    protocols h1 h2 h3

    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
        Content-Security-Policy "default-src 'self'"
        -Server
        -X-Powered-By
    }

    # Static file caching
    @static {
        file
        path *.ico *.css *.js *.gif *.jpg *.jpeg *.png *.svg *.woff *.woff2 *.ttf *.eot *.webp *.avif *.map
    }
    
    header @static {
        Cache-Control "public, max-age=31536000, immutable"
        Expires "1y"
    }

    # Laravel routing
    try_files {path} {path}/ /index.php?{query}

    # Health check
    handle /health {
        respond "OK" 200
    }

    # TLS configuration
    tls {
        protocols tls1.2 tls1.3
        ciphers TLS_AES_128_GCM_SHA256 TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256
    }
}
```

## Database Configuration

### MySQL Configuration (`docker/mysql/conf.d/performance.cnf`)

```ini
[mysqld]
# Connection Settings
max_connections = 200
max_connect_errors = 100000
max_allowed_packet = 64M
interactive_timeout = 3600
wait_timeout = 3600

# Buffer Pool Settings (adjust based on available RAM)
innodb_buffer_pool_size = 1G
innodb_buffer_pool_instances = 4
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M

# Performance Settings
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
innodb_io_capacity = 1000
innodb_io_capacity_max = 2000
innodb_read_io_threads = 8
innodb_write_io_threads = 8

# Query Cache (disabled in MySQL 8.0+)
# query_cache_type = 0
# query_cache_size = 0

# Slow Query Log
slow_query_log = 1
slow_query_log_file = /var/lib/mysql/slow.log
long_query_time = 2
log_queries_not_using_indexes = 1
log_slow_admin_statements = 1

# Binary Logging
log_bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7
max_binlog_size = 100M

# Performance Schema
performance_schema = ON
performance_schema_max_table_instances = 12500
performance_schema_max_table_handles = 4000
```

### Redis Configuration (`docker/redis/redis.conf`)

```redis
# Basic Settings
bind 0.0.0.0
port 6379
timeout 0
keepalive 300

# Memory Management
maxmemory 1gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# AOF (Append Only File)
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Performance Tuning
tcp-backlog 511
tcp-keepalive 300

# I/O Threading (Redis 6.0+)
io-threads 4
io-threads-do-reads yes

# Client Management
maxclients 10000

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Security
protected-mode no
```

## Monitoring Configuration

### Prometheus Configuration (`docker/prometheus/prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"
  - "recording_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: [ 'localhost:9090' ]

  - job_name: 'laravel-app'
    metrics_path: '/metrics'
    static_configs:
      - targets: [ 'nginx:80' ]
    scrape_interval: 30s

  - job_name: 'mysql-exporter'
    static_configs:
      - targets: [ 'mysql-exporter:9104' ]
    scrape_interval: 30s

  - job_name: 'redis-exporter'
    static_configs:
      - targets: [ 'redis-exporter:9121' ]
    scrape_interval: 30s

  - job_name: 'nginx-exporter'
    static_configs:
      - targets: [ 'nginx-exporter:9113' ]
    scrape_interval: 30s
```

### Grafana Data Sources (`docker/grafana/datasources/datasources.yml`)

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
      httpMethod: "POST"

  - name: Elasticsearch
    type: elasticsearch
    url: http://elasticsearch:9200
    access: proxy
    database: "logstash-*"
    interval: Daily
    timeField: "@timestamp"
    editable: true
    jsonData:
      esVersion: "8.15.0"
      timeInterval: "10s"
      maxConcurrentShardRequests: 5

  - name: MySQL
    type: mysql
    url: mysql:3306
    user: laravel
    database: laravel_perf
    editable: true
    jsonData:
      maxOpenConns: 0
      maxIdleConns: 2
      connMaxLifetime: 14400
```

## Load Balancing Configuration

### Nginx Load Balancer (`docker/nginx/load-balancer.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream laravel_backend {
        # Backend servers
        server nginx:80;
        
        # Health checks
        keepalive 32;
    }

    server {
        listen 80;
        server_name localhost;

        # Load balancing
        location / {
            proxy_pass http://laravel_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Performance settings
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 128k;
            proxy_buffers 256 16k;
            proxy_busy_buffers_size 256k;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "load balancer healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### ProxySQL Configuration (`docker/proxysql/proxysql.cnf`)

```ini
datadir = "/var/lib/proxysql"

admin_variables =
{
admin_credentials="admin:admin"
mysql_ifaces="0.0.0.0:6032"
refresh_interval=2000
}

mysql_variables =
{
threads=4
max_connections=2048
default_query_delay=0
default_query_timeout=36000000
have_compress=true
poll_timeout=2000
interfaces="0.0.0.0:6033"
default_schema="information_schema"
stacksize=1048576
server_version="8.0.0"
connect_timeout_server=3000
monitor_username="monitor"
monitor_password="monitor"
monitor_history=600000
monitor_connect_interval=60000
monitor_ping_interval=10000
ping_interval_server_msec=120000
ping_timeout_server=500
commands_stats=true
sessions_sort=true
}

mysql_servers =
(
{
address="mysql"
port=3306
hostgroup=0
status="ONLINE"
weight=900
compression=0
max_replication_lag=10
}
)

mysql_users :
(
{
username = "laravel"
password = "password"
default_hostgroup = 0
max_connections=200
default_schema="laravel_perf"
active = 1
}
)

mysql_query_rules :
(
{
rule_id=1
active=1
match_pattern="^SELECT.*"
destination_hostgroup=0
apply=1
}
)
```

## Environment Variables

### Docker Compose Environment

```bash
# Project naming
PROJECT_NAME=laravel-perf

# Database configuration
DB_ROOT_PASSWORD=rootpassword
DB_NAME=laravel_perf
DB_USER=laravel
DB_PASSWORD=password

# Redis configuration  
REDIS_PASSWORD=

# Monitoring
GRAFANA_ADMIN_PASSWORD=admin

# PHP configuration
PHP_MEMORY_LIMIT=512M
PHP_MAX_EXECUTION_TIME=300
XDEBUG_MODE=develop,debug,profile

# Octane configuration
OCTANE_SERVER=swoole
OCTANE_HOST=0.0.0.0
OCTANE_PORT=8000
OCTANE_WORKERS=4
OCTANE_TASK_WORKERS=6
OCTANE_MAX_REQUESTS=500
```

### Laravel Application Environment

```bash
# Application
APP_NAME="Laravel Performance Test"
APP_ENV=local
APP_KEY=base64:generated-key
APP_DEBUG=true
APP_URL=http://localhost

# Database  
DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE=laravel_perf
DB_USERNAME=laravel
DB_PASSWORD=password

# Cache
CACHE_DRIVER=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379

# Performance monitoring
TELESCOPE_ENABLED=true
DEBUGBAR_ENABLED=true

# Octane
OCTANE_SERVER=swoole
```

## Configuration Relationships

Understanding how configurations interact across services:

### Web Server + PHP Integration

- **Nginx `fastcgi_read_timeout`** must be ≥ **PHP `max_execution_time`**
- **Nginx `client_max_body_size`** should match **PHP `upload_max_filesize`**
- **FrankenPHP worker threads** should align with **PHP-FPM worker processes**

### Database Connection Management

- **MySQL `max_connections`** > **PHP-FPM total workers** + **ProxySQL connections**
- **Connection timeouts** should be consistent across the stack
- **Buffer sizes** should be proportional to expected query complexity

### Monitoring Integration

- **Prometheus scrape intervals** affect metric granularity and resource usage
- **Grafana query timeouts** should accommodate complex metric calculations
- **Alert thresholds** should reflect actual application performance baselines

## Environment-Specific Configurations

The project includes optimized defaults suitable for development and testing. For production deployments:

### Performance Optimizations Needed

- Increase **MySQL buffer pool size** based on available memory
- Tune **PHP OPcache settings** for your application size
- Adjust **web server worker counts** based on CPU cores
- Configure **Redis memory limits** according to cache requirements

### Security Enhancements Required

- Disable **Xdebug** in production environments
- Configure **proper TLS certificates** for FrankenPHP
- Set **restrictive CORS policies** in web server configurations
- Enable **authentication** for monitoring services

## Custom Configuration Override

You can override default configurations by:

1. **Direct file modification** (recommended for permanent changes):

```bash
# Edit configurations directly in docker/ directory
vim docker/nginx/nginx.conf
vim docker/php/conf.d/performance.ini
```

2. **Environment variables** (for runtime adjustments):

```yaml
environment:
  - PHP_MEMORY_LIMIT=1G
  - MYSQL_INNODB_BUFFER_POOL_SIZE=2G
```

3. **Volume mounting** (for temporary testing):

```yaml
volumes:
  - ./custom/nginx.conf:/etc/nginx/nginx.conf
  - ./custom/php.ini:/usr/local/etc/php/php.ini
```

## Configuration Validation

Before starting any stack, validate your configurations:

```bash
# Check all configurations for a specific stack
./stack.sh validate traditional
./stack.sh validate performance
./stack.sh validate enterprise

# Test specific service configurations
nginx -t -c docker/nginx/nginx.conf
php -m | grep opcache
mysql --help | grep innodb-buffer-pool-size
```

## Related Documentation

- **[Configuration Reference Guide](configuration-reference.md)** - Detailed explanations and tuning guidelines
- **[Container Reference](containers.md)** - Service specifications and relationships
- **[Performance Monitoring](monitoring.md)** - Monitoring configuration and metrics
- **[Troubleshooting](troubleshooting.md)** - Configuration-related issue resolution

This configuration system provides flexibility while maintaining optimal performance defaults for Laravel applications.