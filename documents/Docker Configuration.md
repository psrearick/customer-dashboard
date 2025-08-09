# Laravel Performance Testing Docker Environment - Docker Configuration Files

## File Directory Tree

```
laravel-performance-blog/
├── README.md                                    # Project overview and setup instructions
├── .env.example                                 # Environment variables template
├── .gitignore                                   # Git ignore patterns
├── stack.sh                                     # Docker stack management script (executable)
│
├── docker-compose.yml                           # Base services (MySQL, Redis, monitoring)
├── docker-compose.traditional.yml               # Traditional Nginx + PHP-FPM stack
├── docker-compose.frankenphp.yml               # FrankenPHP with PHP 8.4 stack
├── docker-compose.octane.yml                   # Laravel Octane with Swoole stack
├── docker-compose.monitoring.yml               # Enterprise monitoring stack
├── docker-compose.multitenant.yml              # Multi-tenant testing infrastructure
├── docker-compose.database-tools.yml           # Database performance analysis tools
│
└── docker/                                      # Docker configuration directory
    ├── frankenphp/                             # FrankenPHP container configuration
    │   ├── Dockerfile                          # FrankenPHP with PHP 8.4 and extensions
    │   └── Caddyfile                           # Caddy server configuration for FrankenPHP
    │
    ├── php-fpm/                                # Traditional PHP-FPM container
    │   └── Dockerfile                          # PHP 8.4-FPM with performance extensions
    │
    ├── octane/                                 # Laravel Octane container
    │   └── Dockerfile                          # Octane with Swoole/RoadRunner
    │
    ├── nginx/                                  # Nginx web server configuration
    │   ├── nginx.conf                          # Main Nginx configuration
    │   ├── conf.d/                             # Virtual host configurations
    │   │   └── laravel.conf                    # Laravel-specific Nginx config
    │   └── load-balancer.conf                  # Load balancer configuration
    │
    ├── php/                                    # PHP configuration files
    │   └── conf.d/                             # PHP configuration directory
    │       ├── performance.ini                 # General PHP performance settings
    │       ├── opcache.ini                     # OPcache configuration for PHP 8.4
    │       └── xdebug.ini                      # Xdebug profiling configuration
    │
    ├── mysql/                                  # MySQL 8.4 configuration
    │   ├── conf.d/                             # MySQL configuration directory
    │   │   └── performance.cnf                 # MySQL 8.4 performance tuning
    │   └── init/                               # Database initialization scripts
    │       └── 01-create-performance-schema.sql # Performance monitoring setup
    │
    ├── redis/                                  # Redis 8 configuration
    │   └── redis.conf                          # Redis performance configuration
    │
    ├── prometheus/                             # Prometheus monitoring configuration
    │   ├── prometheus.yml                      # Main Prometheus 3.5 configuration
    │   ├── alert_rules.yml                     # Performance alerting rules
    │   └── recording_rules.yml                 # Performance recording rules
    │
    ├── grafana/                                # Grafana dashboard configuration
    │   ├── datasources/                        # Data source configurations
    │   │   └── datasources.yml                 # Prometheus, MySQL, InfluxDB sources
    │   └── dashboards/                         # Dashboard definitions
    │       ├── dashboard.yml                   # Dashboard provisioning config
    │       ├── laravel/                        # Laravel-specific dashboards
    │       │   └── performance-overview.json   # Laravel performance dashboard
    │       └── system/                         # System monitoring dashboards
    │           └── (future system dashboards)
    │
    ├── percona/                                # Percona Toolkit configuration
    │   ├── pt-query-digest.conf               # Query analysis configuration
    │   └── scripts/                            # Analysis scripts
    │       └── analyze-slow-queries.sh         # Automated slow query analysis
    │
    ├── proxysql/                               # ProxySQL database proxy
    │   └── proxysql.cnf                        # ProxySQL configuration for MySQL 8.4
    │
    ├── artillery/                              # Load testing configuration
    │   ├── load-test-config.yml               # Artillery load testing scenarios
    │   └── custom-functions.js                # Custom JavaScript functions for tests
    │
    └── xhprof/                                 # XHProf profiling interface
        └── (XHProf web interface files)
```

## File Descriptions

### **Root Level Files**

| File | Description |
|------|-------------|
| `README.md` | Project overview, setup instructions, and documentation |
| `.env.example` | Template for environment variables |
| `.gitignore` | Git ignore patterns for Laravel and Docker |
| `stack.sh` | **Main Docker management script** - handles all stack operations |

### **Docker Compose Files**

| File | Description |
|------|-------------|
| `docker-compose.yml` | **Base services** - MySQL 8.4, Redis 8, Prometheus, Grafana |
| `docker-compose.traditional.yml` | **Traditional stack** - Nginx + PHP-FPM configuration |
| `docker-compose.frankenphp.yml` | **FrankenPHP stack** - PHP 8.4 with Caddy server |
| `docker-compose.octane.yml` | **Octane stack** - Laravel Octane with Swoole |
| `docker-compose.monitoring.yml` | **Enterprise monitoring** - Elasticsearch, Kibana, APM tools |
| `docker-compose.multitenant.yml` | **Multi-tenant testing** - Multiple databases and Redis clusters |
| `docker-compose.database-tools.yml` | **Database tools** - Percona Toolkit, ProxySQL, analyzers |

### **Docker Configuration Files**

#### **Web Servers & PHP**

| File | Description |
|------|-------------|
| `docker/frankenphp/Dockerfile` | FrankenPHP container with PHP 8.4, extensions, and profiling tools |
| `docker/frankenphp/Caddyfile` | Caddy server configuration with HTTP/3, security headers, worker mode |
| `docker/php-fpm/Dockerfile` | Traditional PHP-FPM container with performance extensions |
| `docker/octane/Dockerfile` | Laravel Octane container with Swoole/RoadRunner |

#### **Nginx Configuration**

| File | Description |
|------|-------------|
| `docker/nginx/nginx.conf` | Main Nginx configuration with security headers and performance tuning |
| `docker/nginx/conf.d/laravel.conf` | Laravel-specific virtual host with CVE-2019-11043 protection |
| `docker/nginx/load-balancer.conf` | Load balancer configuration for multiple app instances |

#### **PHP Configuration**

| File | Description |
|------|-------------|
| `docker/php/conf.d/performance.ini` | General PHP performance settings, memory limits, realpath cache |
| `docker/php/conf.d/opcache.ini` | OPcache configuration optimized for PHP 8.4 with JIT |
| `docker/php/conf.d/xdebug.ini` | Xdebug configuration for profiling and debugging |

#### **Database Configuration**

| File | Description |
|------|-------------|
| `docker/mysql/conf.d/performance.cnf` | MySQL 8.4 performance tuning, buffer pools, slow query log |
| `docker/mysql/init/01-create-performance-schema.sql` | Performance monitoring schema setup |
| `docker/redis/redis.conf` | Redis 8 configuration with I/O threading and persistence |

#### **Monitoring & Profiling**

| File | Description |
|------|-------------|
| `docker/prometheus/prometheus.yml` | Prometheus 3.5 configuration with Laravel-specific metrics |
| `docker/prometheus/alert_rules.yml` | Performance alerting rules for response time, memory, queries |
| `docker/prometheus/recording_rules.yml` | Recording rules for Laravel performance metrics |
| `docker/grafana/datasources/datasources.yml` | Grafana data source configuration |
| `docker/grafana/dashboards/dashboard.yml` | Dashboard provisioning configuration |
| `docker/grafana/dashboards/laravel/performance-overview.json` | Laravel performance dashboard |

#### **Database Tools**

| File | Description |
|------|-------------|
| `docker/percona/pt-query-digest.conf` | Percona Toolkit configuration for query analysis |
| `docker/percona/scripts/analyze-slow-queries.sh` | Automated slow query analysis script |
| `docker/proxysql/proxysql.cnf` | ProxySQL configuration for MySQL 8.4 with connection pooling |

#### **Load Testing**

| File | Description |
|------|-------------|
| `docker/artillery/load-test-config.yml` | Artillery load testing scenarios for performance testing |
| `docker/artillery/custom-functions.js` | Custom JavaScript functions for load testing |

## Quick Start Commands

```bash
# Setup configuration directory structure
./stack.sh setup

# Validate configurations
./stack.sh validate traditional

# Start traditional stack
./stack.sh up traditional -d

# Start full enterprise stack  
./stack.sh up enterprise -d

# Run load tests
./stack.sh up performance -d
docker exec laravel-perf-artillery artillery run /artillery/load-test-config.yml

# View performance metrics
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## Docker Configuration Summary

**Total Docker Files: 30+ configuration files**

### **🚀 Key Components:**

1. **7 Docker Compose files** for different stack combinations
2. **4 Container Dockerfiles** (FrankenPHP, PHP-FPM, Octane, XHProf)
3. **9 Service configuration files** (Nginx, PHP, MySQL, Redis, etc.)
4. **8 Monitoring & profiling configs** (Prometheus, Grafana, Percona)
5. **2 Load testing files** (Artillery scenarios and functions)
6. **1 Management script** (`stack.sh`) with 8 commands

### **🔧 Stack Options:**

- **`traditional`** - Nginx + PHP-FPM (most common)
- **`frankenphp`** - Modern PHP 8.4 with HTTP/3 support
- **`octane`** - Laravel Octane for high performance
- **`performance`** - Traditional + monitoring tools
- **`enterprise`** - Full stack with multi-tenancy and analysis tools
- **`comparison`** - All web servers for benchmarking
- **`full`** - Everything (requires significant resources)

This Docker configuration provides a comprehensive, production-ready environment for Laravel performance testing and optimization with support for multiple architectures and monitoring solutions.