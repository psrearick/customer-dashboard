# Container and Service Reference

This document provides comprehensive details about all containers and services in the Laravel Performance Testing
Environment.

## Overview

The environment consists of **25+ containers** across **7 docker-compose files**, providing a complete testing and
monitoring infrastructure.

## Web Server Containers

### nginx (Traditional Stack)

- **Image**: `nginx:alpine`
- **Container**: `laravel-perf-nginx`
- **Ports**: `80:80`, `443:443`
- **Purpose**: Industry-standard web server for traditional PHP-FPM setups

**Key Features:**

- Alpine Linux base for minimal footprint
- Security headers (HSTS, CSP, X-Frame-Options)
- CVE-2019-11043 protection
- Gzip compression and static file caching
- Custom Laravel routing configuration

**Configuration Files:**

- `docker/nginx/nginx.conf` - Main server configuration
- `docker/nginx/conf.d/laravel.conf` - Laravel-specific virtual host
- `docker/nginx/load-balancer.conf` - Load balancing configuration

### frankenphp (Modern Stack)

- **Image**: Custom build (`docker/frankenphp/Dockerfile`)
- **Container**: `laravel-perf-frankenphp`
- **Ports**: `8080:80`, `8443:443`, `8443:443/udp`
- **Purpose**: Modern PHP server with HTTP/2, HTTP/3, and worker mode

**Key Features:**

- **HTTP/3 Support** via QUIC protocol (UDP port 8443)
- **Worker Mode** for enhanced performance
- **PHP 8.4** with latest performance optimizations
- **Caddy Server** integration with automatic HTTPS
- **Built-in Extensions**: Redis, Xdebug, APCu, XHProf, OPcache

**Unique Configurations:**

- Worker mode: `worker /app/public/index.php`
- Thread management: `num_threads 4`
- TLS protocols: TLS 1.2 and 1.3
- Modern cipher suites and security headers

### octane (High-Performance Stack)

- **Image**: Custom build (`docker/octane/Dockerfile`)
- **Container**: `laravel-perf-octane`
- **Ports**: `8000:8000`
- **Purpose**: Laravel Octane for high-performance, long-running PHP processes

**Key Features:**

- **Swoole Server** for async processing
- **Long-running processes** eliminate bootstrap overhead
- **Task Workers** for background job processing
- **Memory resident** application state
- **Built-in Extensions**: Swoole, Redis, APCu, XHProf

**Performance Configuration:**

- Workers: 4 processes
- Task Workers: 6 processes
- Max Requests: 500 per worker
- Host: `0.0.0.0:8000`

### nginx-lb (Load Balancer)

- **Image**: `nginx:alpine`
- **Container**: `laravel-perf-nginx-lb`
- **Ports**: `8090:80`
- **Purpose**: Load balancer for multi-instance performance testing

**Load Balancing Features:**

- Upstream backend configuration
- Health checks with keepalive
- Proxy headers and timeouts
- Buffer management for high throughput

## PHP Application Containers

### php-fpm (Traditional Application Server)

- **Image**: Custom build (`docker/php-fpm/Dockerfile`)
- **Container**: `laravel-perf-php-fpm`
- **Ports**: `9000:9000`
- **Purpose**: Traditional PHP-FPM application server

**PHP Extensions Installed:**

- **Core**: bcmath, fileinfo, mbstring, pdo_mysql, xml, zip, intl, pcntl, opcache
- **Performance**: Redis, APCu, OPcache with JIT
- **Profiling**: Xdebug, XHProf, Blackfire
- **Base**: PHP 8.4-FPM on Debian Bookworm

**Configuration Files:**

- `docker/php/conf.d/performance.ini` - Memory limits, realpath cache
- `docker/php/conf.d/opcache.ini` - OPcache with JIT compilation
- `docker/php/conf.d/xdebug.ini` - Profiling and debugging settings

## Database Containers

### mysql (Primary Database)

- **Image**: `mysql:8.4`
- **Container**: `laravel-perf-mysql`
- **Ports**: `3306:3306`
- **Purpose**: Primary MySQL database server

**MySQL 8.4 Features:**

- InnoDB performance enhancements
- Improved query optimizer
- Enhanced JSON support
- Performance Schema monitoring

**Configuration:**

- Database: `laravel_perf`
- User: `laravel` / Password: `password`
- Root Password: `rootpassword`
- Custom config: `docker/mysql/conf.d/performance.cnf`

### mysql-tenant-1 & mysql-tenant-2 (Multi-tenant Databases)

- **Image**: `mysql:8.4`
- **Containers**: `laravel-perf-mysql-tenant-1`, `laravel-perf-mysql-tenant-2`
- **Ports**: `3307:3306`, `3308:3306`
- **Purpose**: Separate databases for multi-tenancy testing

**Tenant Configuration:**

- Databases: `tenant_1`, `tenant_2`
- User: `tenant_user` / Password: `tenant_password`
- Isolated storage volumes
- Independent performance monitoring

## Caching Containers

### redis (Primary Cache)

- **Image**: `redis:8-alpine`
- **Container**: `laravel-perf-redis`
- **Ports**: `6379:6379`
- **Purpose**: Primary Redis cache server

**Redis 8 Features:**

- Multi-threaded I/O for better performance
- Improved memory efficiency
- Enhanced persistence options
- Custom config: `docker/redis/redis.conf`

### redis-cluster-1/2/3 (Distributed Cache)

- **Image**: `redis:8-alpine`
- **Containers**: `laravel-perf-redis-cluster-1/2/3`
- **Ports**: `7010:7010`, `7011:7011`, `7012:7012`
- **Purpose**: Three-node Redis cluster for distributed caching

**Cluster Features:**

- Cluster mode enabled
- Automatic failover
- Data sharding across nodes
- Appendonly persistence

## Monitoring Containers

### prometheus (Metrics Collection)

- **Image**: `prom/prometheus:v3.5.0`
- **Container**: `laravel-perf-prometheus`
- **Ports**: `9090:9090`
- **Purpose**: Metrics collection and alerting

**Prometheus 3.5 Features:**

- Enhanced query performance
- Improved memory efficiency
- Advanced alerting rules
- Custom recording rules for Laravel metrics

**Configuration Files:**

- `docker/prometheus/prometheus.yml` - Main configuration
- `docker/prometheus/alert_rules.yml` - Performance alerts
- `docker/prometheus/recording_rules.yml` - Metric recordings

### grafana (Visualization)

- **Image**: `grafana/grafana:latest`
- **Container**: `laravel-perf-grafana`
- **Ports**: `3000:3000`
- **Purpose**: Monitoring dashboards and visualization

**Dashboard Features:**

- Pre-configured data sources (Prometheus, MySQL)
- Laravel performance dashboard
- Public dashboard sharing enabled
- Admin credentials: `admin/admin`

### elasticsearch (Search & Analytics)

- **Image**: `docker.elastic.co/elasticsearch/elasticsearch:8.15.4`
- **Container**: `laravel-perf-elasticsearch`
- **Ports**: `9200:9200`
- **Purpose**: Log aggregation and full-text search

**Elasticsearch 8.15 Configuration:**

- Single-node discovery
- Security disabled for development
- Java heap: 512MB
- Index lifecycle management

### kibana (ELK Dashboard)

- **Image**: `docker.elastic.co/kibana/kibana:8.15.4`
- **Container**: `laravel-perf-kibana`
- **Ports**: `5601:5601`
- **Purpose**: Log visualization and analysis

### jaeger (Distributed Tracing)

- **Image**: `jaegertracing/all-in-one:latest`
- **Container**: `laravel-perf-jaeger`
- **Ports**: `16686:16686` (UI), `14268:14268` (Collector)
- **Purpose**: Distributed request tracing

**Tracing Features:**

- Request flow visualization
- Performance bottleneck identification
- Service dependency mapping
- Zipkin protocol support

## Metrics Exporters

### mysql-exporter (Database Metrics)

- **Image**: `prom/mysqld-exporter:v0.15.1`
- **Container**: `laravel-perf-mysql-exporter`
- **Ports**: `9104:9104`
- **Purpose**: MySQL performance metrics for Prometheus

**Exported Metrics:**

- Query execution statistics
- Connection pool status
- InnoDB buffer pool metrics
- Slow query analysis

**Configuration:**

- Connection: `root:rootpassword@tcp(mysql:3306)/`
- Command-line arguments for authentication

### redis-exporter (Cache Metrics)

- **Image**: `oliver006/redis_exporter`
- **Container**: `laravel-perf-redis-exporter`
- **Ports**: `9121:9121`
- **Purpose**: Redis performance metrics

**Monitored Metrics:**

- Memory usage and fragmentation
- Command execution rates
- Client connections
- Keyspace statistics

### statsd (Custom Metrics)

- **Image**: `prom/statsd-exporter`
- **Container**: `laravel-perf-statsd`
- **Ports**: `9102:9102`, `9125:9125/udp`
- **Purpose**: Application-specific metrics collection

## Database Tools

### percona-toolkit (MySQL Analysis)

- **Image**: `percona/percona-toolkit`
- **Container**: `laravel-perf-percona-toolkit`
- **Purpose**: MySQL performance analysis and optimization

**Available Tools:**

- pt-query-digest for query analysis
- pt-mysql-summary for health checks
- pt-duplicate-key-checker
- Custom analysis scripts

### pt-query-digest (Query Analysis)

- **Image**: `percona/percona-toolkit`
- **Container**: `laravel-perf-pt-query-digest`
- **Purpose**: Automated slow query analysis

**Analysis Features:**

- Slow query log processing
- Query pattern identification
- Performance recommendations
- Automated reporting

### proxysql (Database Proxy)

- **Image**: `proxysql/proxysql:latest`
- **Container**: `laravel-perf-proxysql`
- **Ports**: `6033:6033` (MySQL), `6032:6032` (Admin)
- **Purpose**: MySQL connection pooling and query routing

**ProxySQL Features:**

- Read/write splitting
- Connection multiplexing
- Query caching
- Failover handling
- Configuration: `docker/proxysql/proxysql.cnf`

### pgbouncer (Connection Pooling)

- **Image**: `pgbouncer/pgbouncer:latest`
- **Container**: `laravel-perf-pgbouncer`
- **Ports**: `6432:5432`
- **Purpose**: Database connection pooling

**Pooling Configuration:**

- Pool mode: Transaction-level
- Max client connections: 100
- Default pool size: 25

## Network Architecture

All containers communicate through the `laravel-perf` external network, enabling:

- Service discovery by container name
- Isolated network communication
- Load balancing between services
- Health checks and monitoring

## Volume Management

### Application Volumes

- `./:/var/www/html` (Traditional PHP-FPM)
- `./:/app` (FrankenPHP, Octane)

### Configuration Volumes

- `./docker/mysql/conf.d:/etc/mysql/conf.d`
- `./docker/nginx/conf.d:/etc/nginx/conf.d`
- `./docker/php/conf.d:/usr/local/etc/php/conf.d`

### Data Persistence

- `mysql_data`, `mysql_tenant_1_data`, `mysql_tenant_2_data`
- `redis_data`, `redis_cluster_1/2/3_data`
- `prometheus_data`, `grafana_data`, `elasticsearch_data`

## Performance Optimizations

### PHP Optimizations

- **OPcache**: Bytecode caching with JIT compilation
- **APCu**: User cache for application data
- **Realpath Cache**: Filesystem path optimization
- **Memory Limits**: Optimized for performance testing

### Database Optimizations

- **InnoDB Buffer Pool**: Sized for available memory
- **Query Cache**: Disabled (MySQL 8.4 recommendation)
- **Slow Query Log**: Enabled for analysis
- **Performance Schema**: Full instrumentation

### Web Server Optimizations

- **Worker Processes**: CPU-optimized
- **Connection Handling**: Efficient connection reuse
- **Compression**: Gzip for static assets
- **HTTP/2 & HTTP/3**: Modern protocol support

This comprehensive container setup provides everything needed for thorough Laravel performance testing and optimization.