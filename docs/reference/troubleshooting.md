# Troubleshooting Guide

Common issues and their solutions for the Customer Dashboard project.

## Quick Fixes

### Can't Access the Application

**Symptoms**: Browser shows "Connection refused" or "This site can't be reached"

**Solutions**:

```bash
# 1. Check if containers are running
./bin/stack status

# 2. Restart the stack
./bin/stack restart traditional

# 3. Check the correct URL
# Traditional: http://localhost
# FrankenPHP: http://localhost:8080  
# Octane: http://localhost:8000
```

### "Port Already in Use" Error

**Symptoms**: Error when starting stack: `bind: address already in use`

**Solutions**:

```bash
# 1. Check what's using the port
lsof -i :80
lsof -i :3306

# 2. Stop conflicting services (macOS)
brew services stop nginx
brew services stop mysql

# 3. Or use a different stack
./bin/stack up frankenphp -d    # Uses port 8080
```

### Database Connection Issues

**Symptoms**: "Connection refused" or "Access denied for user" errors

**Solutions**:

```bash
# 1. Ensure MySQL container is running
./bin/stack status

# 2. Check .env file
cat .env | grep DB_
# Should show:
# DB_HOST=mysql
# DB_USERNAME=laravel
# DB_PASSWORD=password

# 3. Test database connection
./bin/dev mysql
# Password: password

# 4. Reset database
./bin/dev artisan migrate:fresh --seed
```

### Frontend Not Loading/Updating

**Symptoms**: Changes to React components not showing, build errors

**Solutions**:

```bash
# 1. Install dependencies
./bin/dev npm install

# 2. Build assets
./bin/dev npm run build

# 3. For development with hot reload
./bin/dev npm run dev

# 4. Clear browser cache
# Open DevTools → Right-click refresh → Empty Cache and Hard Reload
```

### Permission Denied Errors

**Symptoms**: Can't write to storage, cache directories

**Solutions**:

```bash
# Linux/macOS
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache

# If using Docker
chmod +x bin/dev bin/stack
```

## Docker Issues

### Containers Keep Restarting

**Symptoms**: Containers exit and restart repeatedly

**Solutions**:

```bash
# 1. Check logs for errors
./bin/stack logs traditional

# 2. Increase Docker memory (Docker Desktop)
# Settings → Resources → Memory → 4GB minimum

# 3. Clean start
./bin/stack clean
./bin/stack up traditional -d
```

### Out of Disk Space

**Symptoms**: "No space left on device" errors

**Solutions**:

```bash
# 1. Clean Docker system
docker system prune -f

# 2. Remove unused volumes
docker volume prune -f

# 3. Remove old images
docker image prune -f
```

### Slow Container Startup

**Symptoms**: Takes forever to start containers

**Solutions**:

```bash
# 1. Use minimal stack for development
./bin/stack up traditional -d

# 2. Increase Docker resources
# Docker Desktop → Settings → Resources → CPU/Memory

# 3. Disable unnecessary services
# Comment out monitoring services in docker-compose files
```

## Application Issues

### Laravel Errors

**"Key not set" Error**:

```bash
cp .env.example .env
./bin/dev artisan key:generate
```

**"Class not found" Errors**:

```bash
./bin/dev composer install
./bin/dev composer dump-autoload
```

**Migration Errors**:

```bash
# Reset database completely
./bin/dev artisan migrate:fresh --seed

# Or step by step
./bin/dev artisan migrate:reset
./bin/dev artisan migrate
```

**Routing Issues**:

```bash
# Clear route cache
./bin/dev artisan route:clear

# List all routes
./bin/dev artisan route:list
```

### React/Frontend Issues

**TypeScript Errors**:

```bash
# Check types
./bin/dev npm run type-check

# Install missing types
./bin/dev npm install @types/missing-package
```

**Component Not Rendering**:

1. Check browser console for errors
2. Verify component is exported correctly
3. Check import paths
4. Ensure component is registered in Inertia

**Inertia Issues**:

```bash
# Clear Inertia cache
# In browser DevTools → Application → Storage → Clear All

# Verify Inertia middleware is registered
# Check bootstrap/app.php
```

## Development Environment Issues

### Branch Switching Problems

**Symptoms**: Errors after switching git branches

**Solutions**:

```bash
# After switching branches, always run:
git checkout feature/new-branch
./bin/dev composer install
./bin/dev artisan migrate:fresh --seed
./bin/dev npm install
./bin/dev npm run build
```

### Environment Variables Not Working

**Symptoms**: Config values not updating

**Solutions**:

```bash
# Clear config cache
./bin/dev artisan config:clear

# Verify .env file exists
ls -la .env

# Restart stack if needed
./bin/stack restart traditional
```

## Performance Issues

### Slow Application Response

**Symptoms**: Pages load slowly, timeouts

**Solutions**:

```bash
# 1. Enable OPcache (production-like)
# Edit docker/php/conf.d/opcache.ini
# Set opcache.validate_timestamps = 0

# 2. Use Redis for sessions/cache
# In .env:
CACHE_STORE=redis
SESSION_DRIVER=redis

# 3. Optimize Laravel
./bin/dev artisan config:cache
./bin/dev artisan route:cache
./bin/dev artisan view:cache
```

### High Memory Usage

**Symptoms**: System becomes slow, containers killed

**Solutions**:

```bash
# 1. Use traditional stack only (minimal)
./bin/stack up traditional -d

# 2. Reduce MySQL memory
# Edit docker/mysql/conf.d/performance.cnf
# Reduce innodb_buffer_pool_size

# 3. Monitor usage
docker stats
```

## Testing Issues

### Tests Failing

**Database Issues**:

```bash
# Ensure test database is set up
./bin/dev artisan migrate --env=testing

# Or create separate test .env
cp .env .env.testing
# Edit DB_DATABASE=testing_database
```

**Permission Issues**:

```bash
# Fix test file permissions
chmod -R 755 tests/
```

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Look at container logs: `./bin/stack logs traditional`
3. Verify your system meets requirements:
    - Docker 20.10+
    - 4GB RAM minimum
    - 10GB disk space

### What to Include in Bug Reports

```bash
# System info
uname -a
docker --version
docker-compose --version

# Container status
./bin/stack status

# Logs
./bin/stack logs traditional > error-logs.txt
```

### Common "It Works on My Machine" Issues

1. **Different PHP versions**: We use PHP 8.4 in Docker
2. **Missing extensions**: All required extensions are in Docker
3. **File permissions**: Use the provided scripts
4. **Port conflicts**: Use different stacks or stop conflicting services

## Emergency Reset

If everything is broken and you want to start fresh:

```bash
# Nuclear option - removes everything
./bin/stack clean
docker system prune -f
git checkout main
git pull origin main
cp .env.example .env
./bin/stack up traditional -d
./bin/dev composer install
./bin/dev artisan key:generate
./bin/dev artisan migrate:fresh --seed
./bin/dev npm install
./bin/dev npm run build
```

## Preventive Measures

### Daily Development Routine

```bash
# Start of day
./bin/stack up traditional -d
git pull origin main

# End of day  
./bin/stack down traditional
```

### Before Making Changes

```bash
# Backup current state
./bin/dev artisan migrate:status
git status
git stash  # Save uncommitted changes
```

### Before Deploying/Sharing

```bash
# Test everything works
./bin/dev artisan test
./bin/dev npm run type-check
./bin/dev npm run build
```

Most issues are resolved by:

1. Restarting Docker containers
2. Clearing Laravel caches
3. Reinstalling dependencies
4. Checking file permissions

When in doubt, try the emergency reset!