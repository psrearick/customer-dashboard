# Troubleshooting Guide

This guide covers common issues and their solutions when working with the Laravel Performance Testing Environment.

## Common Startup Issues

### Port Conflicts

**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**Diagnosis:**

```bash
# Check what's using the conflicting port
lsof -i :80
lsof -i :3306
lsof -i :6379

# On macOS, check for system services
brew services list | grep started
```

**Solutions:**

```bash
# Stop conflicting services (macOS)
brew services stop nginx
brew services stop mysql  
brew services stop redis

# Stop conflicting services (Linux)
sudo systemctl stop nginx
sudo systemctl stop mysql
sudo systemctl stop redis

# Alternative: Use different ports by modifying docker-compose.yml
```

**Prevention:**

- Use the `stack status` command before starting new stacks
- Stop previous stacks before starting new ones: `stack down [stack]`

### Memory Issues

**Error**: Containers being killed or constantly restarting

**Diagnosis:**

```bash
# Check Docker memory allocation
docker system info | grep -i memory

# Monitor container resource usage
docker stats

# Check system memory
free -h  # Linux
vm_stat  # macOS
```

**Solutions:**

**Docker Desktop (macOS/Windows):**

1. Open Docker Desktop → Settings → Resources → Advanced
2. Increase Memory to at least 8GB (12GB recommended for full stack)
3. Increase CPU cores to 4+ (8+ recommended)
4. Apply & Restart

**Linux:**

```bash
# Add swap space if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Container Startup Failures

**Error**: Container exits immediately or fails to start

**Diagnosis:**

```bash
# Check container logs
docker logs laravel-perf-mysql
docker logs laravel-perf-nginx
docker logs laravel-perf-redis

# Check container status
docker ps -a --filter "label=com.docker.compose.project=laravel-perf"

# Inspect specific container
docker inspect laravel-perf-mysql
```

**Common Solutions:**

**MySQL Container Issues:**

```bash
# Remove existing data volumes and restart
stack clean
stack up traditional -d

# Check MySQL logs specifically
docker logs laravel-perf-mysql 2>&1 | grep -i error

# Access MySQL container for debugging
docker exec -it laravel-perf-mysql mysql -u root -p
```

**Nginx Container Issues:**

```bash
# Test nginx configuration
docker exec laravel-perf-nginx nginx -t

# Check if required config files exist
ls -la docker/nginx/nginx.conf
ls -la docker/nginx/conf.d/laravel.conf
```

## Network and Connectivity Issues

### Service Discovery Problems

**Error**: `could not resolve host: mysql` or similar DNS errors

**Diagnosis:**

```bash
# Check network exists
docker network ls | grep laravel-perf

# Inspect network configuration  
docker network inspect laravel-perf_laravel-perf

# Test connectivity between containers
docker exec laravel-perf-nginx ping mysql
```

**Solutions:**

```bash
# Recreate the network
stack down [stack]
docker network rm laravel-perf_laravel-perf
stack up [stack] -d

# Verify all containers are on the same network
docker inspect laravel-perf-nginx | grep NetworkMode
docker inspect laravel-perf-mysql | grep NetworkMode
```

### Application Not Accessible

**Error**: `Connection refused` or `This site can't be reached`

**Diagnosis:**

```bash
# Check if containers are running
stack status

# Test local connectivity
curl -I http://localhost
curl -I http://localhost:8080  # FrankenPHP
curl -I http://localhost:8000  # Octane

# Check container port mappings
docker port laravel-perf-nginx
```

**Solutions:**

```bash
# Verify port mappings in docker-compose files
cat docker-compose.traditional.yml | grep -A 2 ports

# Check firewall (Linux)
sudo ufw status
sudo iptables -L

# Reset containers
stack restart [stack]
```

## Performance Issues

### Slow Container Startup

**Symptoms**: Containers take a long time to start or become ready

**Diagnosis:**

```bash
# Monitor startup progress
stack logs [stack] -f

# Check resource utilization during startup
docker stats

# Time the startup process
time stack up traditional -d
```

**Solutions:**

```bash
# Increase Docker resources (see Memory Issues above)

# Use pre-built images instead of building
# Comment out 'build:' sections in docker-compose files

# Disable unnecessary services for development
# Start with minimal stack and add services as needed
stack up minimal -d
```

### High Resource Usage

**Symptoms**: System becomes slow, high CPU/memory usage

**Diagnosis:**

```bash
# Identify resource-hungry containers
docker stats --no-stream | sort -k 3 -h

# Check container limits
docker inspect laravel-perf-mysql | grep -i memory

# Monitor system resources
top -p $(docker inspect -f '{{.State.Pid}}' laravel-perf-mysql)
```

**Solutions:**

```bash
# Limit container resources in docker-compose.yml
services:
  mysql:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '2'

# Optimize MySQL configuration
# Edit docker/mysql/conf.d/performance.cnf
innodb_buffer_pool_size = 512M  # Reduce from default

# Use lighter stacks for development
stack up minimal -d
```

## Configuration Issues

### File Permission Problems

**Error**: Permission denied errors, especially on Linux

**Diagnosis:**

```bash
# Check file ownership
ls -la docker/
ls -la storage/  # If using Laravel

# Check Docker daemon permissions
groups $USER | grep docker
```

**Solutions:**

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# Fix file permissions for Laravel
sudo chown -R $USER:www-data storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache

# Use Docker Desktop's file sharing (macOS/Windows)
# Docker Desktop → Settings → File Sharing → Add project directory
```

### Configuration File Not Found

**Error**: `no such file or directory` for config files

**Diagnosis:**

```bash
# Check if configuration files exist
ls -la docker/nginx/nginx.conf
ls -la docker/mysql/conf.d/

# Validate configuration files
stack validate traditional
```

**Solutions:**

```bash
# If configuration files are missing, they should be present in a proper clone
# Check that you cloned the complete repository
git status
git pull origin main

# Check if files were accidentally deleted
git diff --name-status
```

### Environment Variable Issues

**Error**: Variables not being passed to containers

**Diagnosis:**

```bash
# Check environment variables in running container
docker exec laravel-perf-mysql env | grep MYSQL

# Verify docker-compose file syntax
docker-compose -f docker-compose.yml config
```

**Solutions:**

```bash
# Ensure proper YAML indentation in docker-compose files
# Use quotes around values with special characters

environment:
  - "MYSQL_ROOT_PASSWORD=complex!password"

# Restart containers after environment changes
stack restart [stack]
```

## Application-Specific Issues

### Laravel Application Problems

**Database Connection Errors:**

```bash
# Verify database container is running
docker exec laravel-perf-mysql mysql -u root -p -e "SHOW DATABASES;"

# Check Laravel .env configuration
cat .env | grep DB_

# Test connection from PHP container
docker exec laravel-perf-php-fpm php -r "
  try {
    new PDO('mysql:host=mysql;dbname=laravel_perf', 'laravel', 'password');
    echo 'Connection successful';
  } catch(Exception \$e) {
    echo 'Connection failed: ' . \$e->getMessage();
  }
"
```

**Laravel Mix/Asset Issues:**

```bash
# Install and build assets inside container
docker exec laravel-perf-php-fpm composer install
docker exec laravel-perf-php-fpm npm install
docker exec laravel-perf-php-fpm npm run prod
```

### Octane-Specific Issues

**Octane Won't Start:**

```bash
# Check if artisan file exists
docker exec laravel-perf-octane ls -la /app/artisan

# Verify Octane installation
docker exec laravel-perf-octane php artisan octane:status

# Check Swoole extension
docker exec laravel-perf-octane php -m | grep swoole
```

**Memory Leaks in Octane:**

```bash
# Monitor memory usage over time
docker stats laravel-perf-octane

# Reduce max requests per worker
# Edit docker-compose.octane.yml
environment:
  - OCTANE_MAX_REQUESTS=100
```

### FrankenPHP Issues

**Caddyfile Configuration Errors:**

```bash
# Validate Caddyfile syntax
docker exec laravel-perf-frankenphp caddy validate --config /etc/caddy/Caddyfile

# Check FrankenPHP logs
docker logs laravel-perf-frankenphp
```

**Worker Mode Problems:**

```bash
# Check worker status
docker exec laravel-perf-frankenphp ps aux | grep frankenphp

# Disable worker mode temporarily
# Edit docker/frankenphp/Caddyfile - comment out worker line
```

## Monitoring and Logging Issues

### Prometheus Not Collecting Metrics

**Diagnosis:**

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify exporters are running
curl http://localhost:9104/metrics  # MySQL exporter
curl http://localhost:9121/metrics  # Redis exporter
```

**Solutions:**

```bash
# Restart monitoring stack
stack restart performance

# Check Prometheus configuration
docker exec laravel-perf-prometheus cat /etc/prometheus/prometheus.yml
```

### Grafana Dashboard Issues

**Diagnosis:**

```bash
# Check Grafana logs
docker logs laravel-perf-grafana

# Verify data source configuration
curl -u admin:admin http://localhost:3000/api/datasources
```

**Solutions:**

```bash
# Reset Grafana data
docker volume rm laravel-perf_grafana_data
stack restart performance

# Import dashboards manually via UI
# Go to + → Import → Upload JSON file
```

### ELK Stack Problems

**Elasticsearch Issues:**

```bash
# Check Elasticsearch cluster health
curl http://localhost:9200/_cluster/health

# Increase Java heap size if needed
# Edit docker-compose.monitoring.yml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
```

## Advanced Debugging

### Container Introspection

```bash
# Access container shell
docker exec -it laravel-perf-mysql bash
docker exec -it laravel-perf-nginx sh

# Check running processes
docker exec laravel-perf-mysql ps aux

# Monitor container logs in real-time
stack logs performance -f

# Check container filesystem
docker exec laravel-perf-nginx find /etc/nginx -name "*.conf"
```

### Network Debugging

```bash
# Test inter-container connectivity
docker exec laravel-perf-nginx ping mysql
docker exec laravel-perf-php-fpm telnet redis 6379

# Check DNS resolution
docker exec laravel-perf-nginx nslookup mysql

# Inspect network traffic
docker exec laravel-perf-nginx netstat -tulpn
```

### Performance Debugging

```bash
# Monitor system resources
htop  # If available
docker system events  # Watch Docker events

# Profile container startup
docker events --filter container=laravel-perf-mysql &
stack up traditional -d

# Check disk I/O
docker exec laravel-perf-mysql iostat -x 1
```

## Getting Additional Help

### Log Collection for Support

```bash
# Collect all relevant logs
mkdir -p debug-logs
stack logs [stack] > debug-logs/stack-logs.txt
docker system info > debug-logs/docker-info.txt
docker system df > debug-logs/docker-usage.txt

# Create diagnostic script
#!/bin/bash
echo "=== System Info ==="
uname -a
docker --version
docker-compose --version

echo "=== Container Status ==="
stack status

echo "=== Resource Usage ==="
docker stats --no-stream

echo "=== Network Info ==="
docker network ls
docker network inspect laravel-perf_laravel-perf
```

### Useful Commands for Support

```bash
# System information
docker system info
docker system df

# Container information  
docker ps -a --filter "label=com.docker.compose.project=laravel-perf"
docker inspect laravel-perf-mysql

# Network information
docker network ls
docker port laravel-perf-nginx

# Resource usage
docker stats --no-stream
```

### When to Report Issues

Before reporting issues to the project repository:

1. Verify system requirements are met
2. Try with minimal stack first
3. Check this troubleshooting guide
4. Collect diagnostic information
5. Test with clean environment (`stack clean`)

Include in your issue report:

- Operating system and Docker versions
- Stack configuration being used
- Complete error messages and logs
- Steps to reproduce the issue
- System resource information

Most issues are related to insufficient system resources or port conflicts, which can be resolved by following the
solutions in this guide.