# Laravel Performance Testing Docker Environment

A comprehensive Docker-based environment for Laravel performance testing, optimization, and blog content creation. This setup provides multiple web server configurations, monitoring tools, and profiling capabilities for systematic performance analysis.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard

# 2. Create configuration structure
chmod +x stack.sh
./stack.sh setup

# 3. Create environment file
cp .env.example .env

# 4. Start traditional stack
./stack.sh up traditional -d

# 5. Visit your application
open http://localhost
```

## Available Stacks

| Stack         | Description                | Use Case                                |
|---------------|----------------------------|-----------------------------------------|
| `traditional` | Nginx + PHP-FPM            | Most common production setup            |
| `frankenphp`  | FrankenPHP + Caddy         | Modern HTTP/3 with worker mode          |
| `octane`      | Laravel Octane + Swoole    | High-performance long-running processes |
| `performance` | Traditional + monitoring   | Performance testing with metrics        |
| `enterprise`  | Full stack + multi-tenancy | Enterprise features and analysis        |
| `comparison`  | All web servers            | Benchmarking different configurations   |
| `full`        | Everything enabled         | Complete testing environment            |

## Stack Management

```bash
# Setup and validation
./stack.sh setup                    # Create directory structure
./stack.sh validate traditional     # Check configuration files

# Stack operations
./stack.sh up performance -d        # Start with background mode
./stack.sh down enterprise          # Stop specific stack
./stack.sh restart frankenphp       # Restart stack
./stack.sh logs octane              # View logs

# System management
./stack.sh status                   # Show running containers
./stack.sh clean                    # Remove all containers/volumes
```

## Configuration

### Environment Variables

Create `.env` file with:

```bash
# Database
DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE=laravel_perf
DB_USERNAME=laravel
DB_PASSWORD=password

# Cache
REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379

# Performance
OCTANE_SERVER=swoole
XDEBUG_MODE=develop,debug,profile
```

### Stack-Specific Configuration

Each stack uses specific configuration files:

- **Traditional:** `docker/nginx/` and `docker/php-fpm/`
- **FrankenPHP:** `docker/frankenphp/Caddyfile`
- **Octane:** `docker/octane/` for Swoole configuration
- **Monitoring:** `docker/prometheus/` and `docker/grafana/`

## Performance Monitoring

### Access Monitoring Tools

- **Grafana Dashboard:** http://localhost:3000 (admin/admin)
- **Prometheus Metrics:** http://localhost:9090
- **XHProf Profiling:** http://localhost:8080
- **Kibana (ELK):** http://localhost:5601

### Load Testing

```bash
# Start performance stack
./stack.sh up performance -d

# Run load tests
docker exec laravel-perf-artillery artillery run /artillery/load-test-config.yml

# View results in Grafana
open http://localhost:3000
```

## Performance Testing Features

### Web Server Comparison

Test and compare:
- **Traditional:** Nginx + PHP-FPM
- **Modern:** FrankenPHP with HTTP/3 and worker mode
- **High-Performance:** Laravel Octane with Swoole

### Monitoring & Profiling

- **Prometheus:** Metrics collection and alerting
- **Grafana:** Performance dashboards and visualization
- **XHProf:** Detailed PHP function profiling
- **Xdebug:** Step debugging and performance analysis
- **Percona Toolkit:** MySQL query analysis

### Database Performance

- **MySQL 8.4:** Latest performance features
- **Redis 8:** Advanced caching with I/O threading
- **ProxySQL:** Connection pooling and query routing
- **Query Analysis:** Automated slow query detection

## 🏗️ Architecture

### Multi-Environment Support

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Traditional   │    │    FrankenPHP    │    │     Octane      │
│  Nginx+PHP-FPM  │    │   Caddy+Worker   │    │  Swoole+Tasks   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
   ┌────▼────┐             ┌─────▼─────┐            ┌─────▼──────┐
   │  MySQL  │             │   Redis   │            │ Monitoring │
   │   8.4   │             │     8     │            │   Stack    │
   └─────────┘             └───────────┘            └────────────┘
```

### Performance Testing Pipeline

1. **Baseline Measurement:** Intentionally poor performance
2. **Query Optimization:** Relationship loading improvements
3. **Database Optimization:** Strategic indexing
4. **Memory Optimization:** Efficient data processing
5. **Caching Implementation:** Multi-layer caching strategy

## 🔬 Blog Content Integration

This environment supports systematic performance optimization content:

### Performance Metrics

- Response time improvements (target: >90% reduction)
- Query count optimization (target: >95% reduction)
- Memory usage efficiency (target: >75% reduction)
- Throughput increases (target: >10x improvement)

### Reproducible Examples

All blog content includes:
- Working code examples from demonstration branches
- Concrete before/after measurements
- Step-by-step optimization guides
- Environment setup for reader validation

## Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check what's using ports
sudo lsof -i :80,:3000,:9090
# Stop conflicting services or change ports
```

**Permission Issues**
```bash
# Fix Laravel storage permissions
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache
```

**Memory Issues**
```bash
# Increase Docker memory limit (Docker Desktop)
# Recommended: 8GB+ for full stack
```

### Performance Debugging

```bash
# Check container resource usage
docker stats

# View specific service logs
./stack.sh logs performance

# Access container for debugging
docker exec -it laravel-perf-mysql mysql -u root -p
```

## Documentation

### File Structure

- `docker/` - All Docker configurations
- `stack.sh` - Main management script
- `docker-compose.*.yml` - Stack definitions

### Configuration Files

- **PHP:** `docker/php/conf.d/` - Performance, OPcache, Xdebug
- **MySQL:** `docker/mysql/conf.d/` - Performance tuning
- **Nginx:** `docker/nginx/` - Security and performance
- **Monitoring:** `docker/prometheus/`, `docker/grafana/`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-optimization`)
3. Test changes with `./stack.sh validate [stack]`
4. Commit changes (`git commit -am 'Add amazing optimization'`)
5. Push to branch (`git push origin feature/amazing-optimization`)
6. Create Pull Request

## License

This project is open-sourced software licensed under the [_MIT license_](LICENSE).
