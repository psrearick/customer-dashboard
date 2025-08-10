# Getting Started Guide

This guide will walk you through setting up and using the Customer Dashboard app for the first time.

## Prerequisites

### System Requirements

**Minimum Requirements:**

- Docker 20.10+ and Docker Compose 2.0+
- 4GB RAM (8GB recommended for full stack)
- 4 CPU cores (8 cores recommended)
- 10GB free disk space

**Recommended for Full Testing:**

- 12GB RAM
- 8+ CPU cores
- 20GB free disk space
- SSD storage for better I/O performance

### Software Installation

**macOS:**

```bash
# Install Docker Desktop
brew install --cask docker

# Verify installation
docker --version
docker-compose --version
```

**Linux (Ubuntu/Debian):**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard
```

### 2. Make Stack Script Executable

```bash
chmod +x stack.sh
```

### 3. Verify Configuration Files

```bash
# Validate that all configuration files exist for the traditional stack
./stack.sh validate traditional

# Expected output:
# ✓ Nginx configuration found
# ✓ Prometheus configuration found
# Configuration validation complete
```

## First Run

### Start with Traditional Stack

The traditional stack (Nginx + PHP-FPM) is the most common and stable configuration:

```bash
# Start traditional stack in background mode
./stack.sh up traditional -d

# Check container status
./stack.sh status
```

Expected output:

```
Running containers:
NAMES                         STATUS                   PORTS
laravel-perf-nginx            Up 30 seconds           0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
laravel-perf-php-fpm          Up 31 seconds           9000/tcp
laravel-perf-mysql            Up 32 seconds           0.0.0.0:3306->3306/tcp, 33060/tcp
laravel-perf-redis            Up 32 seconds           0.0.0.0:6379->6379/tcp
laravel-perf-prometheus       Up 32 seconds           0.0.0.0:9090->9090/tcp
laravel-perf-grafana          Up 31 seconds           0.0.0.0:3000->3000/tcp
```

### Access Your Services

Once containers are running, access these URLs:

- **Application**: http://localhost
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Next Steps

### 1. Explore Different Stacks

```bash
# Try modern FrankenPHP stack
./stack.sh down traditional
./stack.sh up frankenphp -d

# Access FrankenPHP on port 8080
open http://localhost:8080

# Try high-performance Octane stack  
./stack.sh down frankenphp
./stack.sh up octane -d

# Access Octane on port 8000
open http://localhost:8000
```

### 2. Enable Full Monitoring

```bash
# Start performance stack (traditional + monitoring tools)
./stack.sh down octane
./stack.sh up performance -d
```

Additional services available:

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Jaeger Tracing**: http://localhost:16686

### 3. Compare All Stacks

```bash
# Start comparison stack (all web servers + monitoring)
./stack.sh down performance
./stack.sh up comparison -d
```

Access all web servers simultaneously:

- **Nginx**: http://localhost:80
- **FrankenPHP**: http://localhost:8080
- **Octane**: http://localhost:8000

## Working with the Laravel Application

### Laravel 12 + React 19 Setup

This project includes a complete Laravel 12 application with React 19 and Inertia.js:

```bash
# Start traditional stack (or the stack of your choice) in background mode
./stack.sh up traditional -d

# Configure database connection
cp .env.example .env

# Install dependencies and setup
composer install
php artisan key:generate
php artisan migrate --seed

# Install frontend dependencies and build assets
npm install
npm run build

# Or start development server with hot reloading
npm run dev
```

### Application Structure

The application uses modern React 19 with Inertia.js for seamless SPA experience:

- **Frontend**: React 19 with TypeScript in `resources/js/`
- **Components**: Radix UI components in `resources/js/Components/`
- **Pages**: Inertia pages in `resources/js/Pages/`
- **Layouts**: Reusable layouts in `resources/js/Layouts/`

### Available Application Routes

- `/` - Welcome page with technology showcase
- `/dashboard` - Sample dashboard with Radix UI components  
- `/health` - Health check endpoint (JSON response)

### Laravel with Octane

Laravel Octane is pre-installed and configured:

```bash
# Octane is already installed with Swoole driver
# Configuration is handled by Docker
# Starting the octane container starts octane automatically
./stack.sh up octane -d
```

## Performance Testing Workflow

### 1. Establish Baseline

```bash
# Start performance monitoring stack
./stack.sh up performance -d

# Wait for all services to be ready
sleep 30

# Run baseline performance test
docker run --rm --network laravel-perf_laravel-perf \
  artilleryio/artillery:latest \
  quick --count 100 --num 10 http://nginx/
```

### 2. Monitor Results

Open Grafana dashboard at http://localhost:3000:

- Login: admin/admin
- Navigate to Laravel Performance Overview
- Observe baseline metrics

### 3. Compare Configurations

```bash
# Test FrankenPHP performance
./stack.sh down performance
./stack.sh up comparison -d

# Run tests against different servers
docker run --rm --network laravel-perf_laravel-perf \
  artilleryio/artillery:latest \
  quick --count 100 --num 10 http://nginx/

docker run --rm --network laravel-perf_laravel-perf \
  artilleryio/artillery:latest \
  quick --count 100 --num 10 http://frankenphp:80/

docker run --rm --network laravel-perf_laravel-perf \
  artilleryio/artillery:latest \
  quick --count 100 --num 10 http://octane:8000/
```

## Common First-Time Issues

### Port Conflicts

If you see "port already in use" errors:

```bash
# Check what's using port 80
lsof -i :80

# Stop conflicting services (macOS)
sudo brew services stop nginx
sudo brew services stop apache2

# Or use different ports by modifying docker-compose files
```

### Memory Issues

If containers are killed or restarting:

```bash
# Check Docker memory settings (Docker Desktop)
# Go to Preferences → Resources → Memory
# Increase to at least 8GB for full stack

# Check container resource usage
docker stats
```

### Permission Issues

If you encounter file permission errors:

```bash
# Fix Laravel storage permissions (if using Laravel)
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache

# For macOS with Docker Desktop, ensure file sharing is enabled
# Docker Desktop → Preferences → File Sharing
```

### Container Startup Failures

```bash
# Check logs for specific failures
docker logs laravel-perf-mysql
docker logs laravel-perf-nginx

# Restart the problematic stack
./stack.sh restart traditional

# Clean restart (removes containers and volumes)
./stack.sh clean
./stack.sh up traditional -d
```

## Development Workflow

### Daily Development

```bash
# Start your preferred stack for development
./stack.sh up traditional -d

# Work on your application...

# Stop when done
./stack.sh down traditional
```

### Performance Testing Session

```bash
# Start comprehensive monitoring
./stack.sh up enterprise -d

# Run your tests and optimizations...

# Clean up
./stack.sh clean
```

### Debugging Issues

```bash
# View real-time logs
./stack.sh logs performance -f

# Access container shells
docker exec -it laravel-perf-mysql bash
docker exec -it laravel-perf-nginx sh

# Check container networking  
docker network ls
docker network inspect laravel-perf_laravel-perf
```

## Next Documentation

Once you're comfortable with the basics:

- **[Stack Management](stack-management.md)** - Detailed stack operations
- **[Container Reference](containers.md)** - Complete container documentation
- **[Configuration Guide](configuration.md)** - Advanced configuration options
- **[Performance Monitoring](monitoring.md)** - Deep dive into monitoring tools
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Verify your system meets the requirements
3. Ensure Docker has sufficient resources allocated
4. Check container logs for specific error messages
5. Open an issue on the [GitHub repository](https://github.com/psrearick/customer-dashboard/issues)

The performance testing environment is designed to be comprehensive yet approachable. Start with the traditional stack
and gradually explore more advanced configurations as you become comfortable with the system.