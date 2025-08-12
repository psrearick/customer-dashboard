# Troubleshooting

This guide covers the most common issues you'll encounter when setting up and running the customer management
application.

## Quick Fixes (Most Common Issues)

### Can't Access the Application

**Problem:** Browser shows "Connection refused" or "This site can't be reached"

**Solutions:**

```bash
# Check if containers are running
./bin/stack status

# Restart the stack
./bin/stack restart traditional

# Verify you're using the correct URL:
# Traditional: http://localhost
# FrankenPHP: http://localhost:8080
# Octane: http://localhost:8000
```

### Port Already in Use

**Problem:** Error like `bind: address already in use` when starting containers

**Solutions:**

```bash
# Check what's using the port
lsof -i :80
lsof -i :3306

# Stop conflicting services (macOS)
brew services stop nginx
brew services stop mysql

# Stop conflicting services (Linux)
sudo systemctl stop nginx
sudo systemctl stop mysql

# Alternative: Use a different stack
./bin/stack up frankenphp -d    # Uses port 8080 instead of 80
```

### Containers Won't Start or Keep Restarting

**Problem:** Containers exit immediately or restart repeatedly

**Solutions:**

```bash
# Check container logs for errors
./bin/stack logs traditional

# Increase Docker memory allocation
# Docker Desktop → Settings → Resources → Memory → 6GB+

# Clean start
./bin/stack clean
./bin/stack up traditional -d
```

### Permission Denied Errors

**Problem:** Can't write to files or execute scripts

**Solutions:**

```bash
# Make scripts executable
chmod +x bin/dev bin/stack

# Fix Laravel storage permissions (Linux/macOS)
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in after this command
```

## Docker Issues

### Out of Memory Errors

**Problem:** Containers being killed or system becomes slow

**Solutions:**

1. **Docker Desktop (macOS/Windows):**
    - Open Docker Desktop → Settings → Resources
    - Increase Memory to at least 6GB (8GB+ for performance stack)
    - Increase CPU cores to 4+
    - Apply & Restart

2. **Use minimal stack:**
   ```bash
   ./bin/stack up traditional -d  # Instead of performance stack
   ```

### Containers Exiting Immediately

**Problem:** Container starts then exits with error codes

**Diagnosis:**

```bash
# Check specific container logs
docker logs laravel-perf-mysql
docker logs laravel-perf-nginx
docker logs laravel-perf-redis

# Check container status
docker ps -a
```

**Solutions:**

```bash
# Remove problematic volumes and restart
./bin/stack clean
./bin/stack up traditional -d

# For MySQL issues specifically
docker volume rm laravel-perf_mysql_data
./bin/stack up traditional -d
```

### Slow Startup Times

**Problem:** Takes a long time for containers to become ready

**Solutions:**

```bash
# Monitor startup progress
./bin/stack logs traditional -f

# Use traditional stack (lightest option)
./bin/stack up traditional -d

# Increase Docker resources (see memory section above)
```

## Application Issues

### Database Connection Failures

**Problem:** Laravel shows database connection errors

**Solutions:**

```bash
# Verify MySQL container is running
docker ps | grep mysql

# Check database credentials in .env file
cat .env | grep DB_

# Test database connection
./bin/dev mysql
# Password: password

# Reset database completely
./bin/dev artisan migrate:fresh --seed
```

### Laravel Key Not Set Errors

**Problem:** "No application encryption key has been specified"

**Solution:**

```bash
./bin/dev artisan key:generate
```

### Frontend Assets Not Loading

**Problem:** CSS/JavaScript not working, or build errors

**Solutions:**

```bash
# Check if Node container is running
docker ps | grep node

# Rebuild assets
./bin/dev npm install
./bin/dev npm run build

# For development with auto-reload
./bin/dev npm run dev

# Check Node container logs
docker logs laravel-perf-node
```

### 500 Errors After Switching Branches

**Problem:** Application breaks after git checkout

**Solutions:**

```bash
# Always run after switching branches:
./bin/dev composer install
./bin/dev artisan migrate:fresh --seed
./bin/dev npm install
./bin/dev npm run build

# Clear Laravel caches
./bin/dev artisan cache:clear
./bin/dev artisan config:clear
./bin/dev artisan view:clear
```

## When Switching Branches

### Database Migration Issues

**Problem:** Migration errors or missing tables

**Solution:**

```bash
# Fresh start with new branch
./bin/dev artisan migrate:fresh --seed
```

### Dependency Conflicts

**Problem:** Composer or npm errors after branch switch

**Solutions:**

```bash
# Update PHP dependencies
./bin/dev composer install

# Update Node dependencies
./bin/dev npm install

# If still having issues, clear caches
./bin/dev composer dump-autoload
```

### Cache Problems

**Problem:** Old data or configuration persisting

**Solution:**

```bash
# Clear all Laravel caches
./bin/dev artisan optimize:clear

# Or individually:
./bin/dev artisan cache:clear
./bin/dev artisan config:clear
./bin/dev artisan route:clear
./bin/dev artisan view:clear
```

## Getting More Information

### Check Container Status

```bash
# See what's running
./bin/stack status

# More detailed container info
docker ps -a

# Check resource usage
docker stats
```

### View Logs

```bash
# All logs for a stack
./bin/stack logs traditional

# Follow logs in real-time
./bin/stack logs traditional -f

# Specific container logs
docker logs laravel-perf-mysql
docker logs laravel-perf-nginx
docker logs laravel-perf-node
```

### Check Port Usage

```bash
# See what's using common ports
lsof -i :80    # Web server
lsof -i :3306  # MySQL
lsof -i :6379  # Redis
lsof -i :5173  # Vite dev server

# Check Docker port mappings
docker port laravel-perf-nginx
```

## Nuclear Option

When everything is broken and you want to start completely fresh:

```bash
# WARNING: This removes all containers, volumes, and data
./bin/stack clean

# Clean Docker system (removes unused data)
docker system prune -f

# Start over
git checkout main
cp .env.example .env
./bin/stack up traditional -d
./bin/dev artisan key:generate
./bin/dev composer install
./bin/dev artisan migrate:fresh --seed
./bin/dev npm install
./bin/dev npm run build
```

**This will delete:**

- All project containers
- All project data volumes (database data, etc.)
- Any uncommitted changes in containers

## Still Having Problems?

### Before Asking for Help

1. Try the nuclear option above
2. Verify your system meets the prerequisites
3. Check that Docker Desktop is running and has sufficient resources

### Collect Diagnostic Information

```bash
# System information
docker --version
docker-compose --version
./bin/stack status

# Save logs for troubleshooting
./bin/stack logs traditional > debug-logs.txt
```

### Common "It Works on My Machine" Issues

- **Different operating systems:** Use Docker exactly as documented
- **Insufficient resources:** Increase Docker memory/CPU allocation
- **Port conflicts:** Stop other services or use different stacks
- **File permissions:** Follow the permission fix commands above

### Getting Help

- **Check logs first:** Most issues show clear error messages in logs
- **Try different stack:** If traditional doesn't work, try frankenphp
- **Reset everything:** The nuclear option fixes 90% of persistent issues

Most problems are resolved by ensuring Docker has enough resources and using the reset commands when switching between
branches or after making changes.