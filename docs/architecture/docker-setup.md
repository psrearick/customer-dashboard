# Docker Setup Guide

This guide explains the Docker setup for the Customer Dashboard project and why Docker was chosen for the development
environment.

## Why Docker?

Docker provides several benefits for a learning/reference project:

1. **Consistency**: Everyone gets the same environment, regardless of their OS
2. **No conflicts**: Isolated from other projects on your machine
3. **Easy switching**: Test different PHP versions, web servers, etc.
4. **Production-like**: Learn deployment patterns that work in real production
5. **Clean machine**: No need to install MySQL, Redis, PHP locally

## Quick Start

```bash
# Start the standard development environment
./bin/stack up traditional -d

# Run Laravel commands
./bin/dev artisan migrate
./bin/dev composer install
./bin/dev npm install

# Stop everything
./bin/stack down traditional
```

## Available Stacks

### Traditional Stack (Recommended for Learning)

**Command**: `./bin/stack up traditional -d`  
**Components**: Nginx + PHP-FPM + MySQL + Redis  
**Port**: http://localhost  
**Why use**: This is what most Laravel apps use in production

### Modern Stack (FrankenPHP)

**Command**: `./bin/stack up frankenphp -d`  
**Components**: FrankenPHP + MySQL + Redis  
**Port**: http://localhost:8080  
**Why use**: Experiment with cutting-edge PHP server technology

### High-Performance Stack (Octane)

**Command**: `./bin/stack up octane -d`  
**Components**: Laravel Octane + Swoole + MySQL + Redis  
**Port**: http://localhost:8000  
**Why use**: Learn how to maximize Laravel performance

## Essential Commands

### Stack Management

```bash
./bin/stack up [stack] -d    # Start a stack in background
./bin/stack down [stack]      # Stop a stack
./bin/stack status           # See what's running
./bin/stack logs [stack] -f  # View logs
./bin/stack clean            # Remove everything and start fresh
```

### Development Helper (dev)

```bash
./bin/dev artisan [command]  # Run Artisan commands
./bin/dev composer [command] # Run Composer
./bin/dev npm [command]      # Run NPM
./bin/dev mysql             # Access MySQL CLI
./bin/dev shell             # Get a shell in the PHP container
```

## Understanding the Setup

### File Structure

```
docker/                 # All Docker configurations
├── mysql/             # MySQL configurations
├── nginx/             # Nginx web server configs
├── php/               # PHP configurations
├── php-fpm/           # PHP-FPM Dockerfile
├── frankenphp/        # FrankenPHP setup
└── octane/            # Octane setup

docker-compose.yml      # Base services (MySQL, Redis)
docker-compose.*.yml    # Stack-specific configurations
```

### How It Works

1. **Base Layer** (`docker-compose.yml`): Defines core services all stacks need
2. **Stack Layer** (`docker-compose.traditional.yml`): Adds stack-specific services
3. **Network**: All containers share a network for inter-service communication
4. **Volumes**: Your code is mounted into containers, changes are instant

### Service Connections

Your Laravel app connects to services using these hostnames:

- **MySQL**: `mysql` (port 3306)
- **Redis**: `redis` (port 6379)
- **Nginx**: `nginx` (port 80)

These are configured in your `.env` file:

```env
DB_HOST=mysql
REDIS_HOST=redis
```

## Common Tasks

### First Time Setup

```bash
# 1. Clone the project
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard

# 2. Start Docker environment
./bin/stack up traditional -d

# 3. Install dependencies
./bin/dev composer install
./bin/dev npm install

# 4. Set up Laravel
cp .env.example .env
./bin/dev artisan key:generate
./bin/dev artisan migrate --seed

# 5. Build frontend
./bin/dev npm run build
```

### Daily Development

```bash
# Start your environment
./bin/stack up traditional -d

# Start Vite dev server (in separate terminal)
./bin/dev npm run dev

# Make changes, they auto-reload!

# When done for the day
./bin/stack down traditional
```

### Switching Stacks

```bash
# Stop current stack
./bin/stack down traditional

# Start different stack
./bin/stack up octane -d

# Your code is the same, just served differently!
```

### Database Tasks

```bash
# Fresh database with seeders
./bin/dev artisan migrate:fresh --seed

# Access MySQL directly
./bin/dev mysql
# Password: password

# Backup database
./bin/dev bash -c "mysqldump -h mysql -u laravel -ppassword laravel_perf > backup.sql"
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 80
lsof -i :80

# Use a different stack (different ports)
./bin/stack up frankenphp -d  # Uses port 8080
```

### Containers Won't Start

```bash
# Clean slate approach
./bin/stack clean
./bin/stack up traditional -d

# Check logs
./bin/stack logs traditional
```

### Permission Issues (Linux)

```bash
# Fix storage permissions
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache
```

### Out of Memory

Docker Desktop → Preferences → Resources → Memory → Increase to 4GB minimum

## Performance Tuning

### For Learning/Development

The default settings are optimized for development:

- File changes are detected immediately
- Error messages are verbose
- Caching is minimal for accurate debugging

### For Testing Production-like Performance

```bash
# Use the Octane stack
./bin/stack up octane -d

# Or enable OPcache fully
# Edit docker/php/conf.d/opcache.ini
# Set opcache.validate_timestamps = 0
```

## Understanding the Configuration

### PHP Configuration

**Files**: `docker/php/conf.d/*.ini`  
**Purpose**: Control memory limits, timeouts, extensions  
**When to modify**: Debugging issues, testing limits

### MySQL Configuration

**Files**: `docker/mysql/conf.d/*.cnf`  
**Purpose**: Database performance tuning  
**When to modify**: Testing query optimization

### Web Server Configuration

**Files**: `docker/nginx/conf.d/*.conf`  
**Purpose**: Request handling, caching, routing  
**When to modify**: Testing different server setups

## Advanced Usage

### Adding Services

To add a new service (e.g., Elasticsearch):

1. Add to `docker-compose.yml` or create new compose file
2. Update network configuration
3. Add environment variables to `.env`

### Custom PHP Extensions

Edit the appropriate Dockerfile:

- `docker/php-fpm/Dockerfile` for traditional stack
- `docker/frankenphp/Dockerfile` for FrankenPHP
- `docker/octane/Dockerfile` for Octane

### Production Deployment

While this Docker setup is for development, the patterns you learn here apply to production:

- Container orchestration (Kubernetes)
- Service discovery
- Environment-based configuration
- Health checks and monitoring

## Why Multiple Stacks?

Each stack teaches different deployment strategies:

1. **Traditional**: How 90% of Laravel apps are deployed
2. **FrankenPHP**: Next-generation PHP serving
3. **Octane**: Maximum performance techniques

By switching between them, you learn:

- Performance characteristics
- Configuration differences
- Optimization strategies
- When to use each approach

## Further Reading

- [Architecture Overview](overview.md) - Why these choices were made
- [Configuration Guide](configuration-guide.md) - Detailed configuration options
- [Docker Documentation](https://docs.docker.com/) - Official Docker docs

Remember: This Docker setup is a learning tool. Start with the traditional stack, understand how it works, then explore
the others as you learn more about Laravel deployment options.