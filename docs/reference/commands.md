# Command Reference

Quick reference for the most commonly used commands in this project.

## Project Setup Commands

```bash
# Initial setup
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard
./bin/stack up traditional -d
./bin/dev composer install
./bin/dev artisan key:generate
./bin/dev artisan migrate --seed
./bin/dev npm install
./bin/dev npm run build

# Access application
open http://localhost
```

## Stack Management

```bash
# Start stacks
./bin/stack up traditional -d      # Standard development stack
./bin/stack up frankenphp -d       # Modern HTTP/3 stack  
./bin/stack up octane -d           # High-performance stack

# Stop stacks
./bin/stack down traditional       # Stop specific stack
./bin/stack stop-all               # Stop all containers

# Stack information
./bin/stack status                 # See running containers
./bin/stack logs traditional -f    # Follow logs
./bin/stack list                   # Available stacks

# Clean up
./bin/stack clean                  # Remove everything
```

## Development Commands

### Laravel Artisan

```bash
./bin/dev artisan migrate          # Run migrations
./bin/dev artisan migrate:fresh    # Fresh migration
./bin/dev artisan migrate:fresh --seed  # Fresh with seeders
./bin/dev artisan tinker           # Interactive shell
./bin/dev artisan route:list       # List routes
./bin/dev artisan make:controller UserController  # Create controller
./bin/dev artisan make:model Post  # Create model
./bin/dev artisan make:request UserRequest        # Create form request
./bin/dev artisan make:test UserTest               # Create test
./bin/dev artisan queue:work       # Process jobs
./bin/dev artisan cache:clear      # Clear cache
./bin/dev artisan config:clear     # Clear config cache
./bin/dev artisan view:clear       # Clear view cache
```

### Composer

```bash
./bin/dev composer install         # Install dependencies
./bin/dev composer update          # Update dependencies
./bin/dev composer require package/name   # Add package
./bin/dev composer dump-autoload   # Regenerate autoloader
./bin/dev composer test            # Run tests (if configured)
```

### NPM/Frontend

```bash
./bin/dev npm install              # Install node packages
./bin/dev npm run dev              # Start Vite dev server
./bin/dev npm run build            # Build for production
./bin/dev npm run type-check       # TypeScript checking
```

### Database Access

```bash
./bin/dev mysql                    # MySQL CLI (password: password)
./bin/dev redis-cli                # Redis CLI
```

### Container Access

```bash
./bin/dev shell                    # PHP container shell
./bin/dev bash                     # Alias for shell
```

## Branch Operations

```bash
# List branches
git branch -a                      # Local and remote branches

# Switch branches  
git checkout main                  # Go to main branch
git checkout feature/repository-pattern  # Go to feature branch

# After switching branches
./bin/dev artisan migrate:fresh --seed   # Reset database
./bin/dev composer install               # Install dependencies
./bin/dev npm install                    # Install frontend deps
./bin/dev npm run build                  # Build assets
```

## Testing Commands

```bash
./bin/dev artisan test             # Run all tests
./bin/dev artisan test --filter UserTest  # Run specific test
./bin/dev vendor/bin/phpunit       # PHPUnit directly
./bin/dev vendor/bin/phpunit --coverage-html coverage  # Coverage report
```

## Performance Commands

```bash
# Laravel optimizations
./bin/dev artisan config:cache     # Cache configuration
./bin/dev artisan route:cache      # Cache routes
./bin/dev artisan view:cache       # Cache views
./bin/dev artisan optimize         # Run all optimizations

# Clear optimizations (development)
./bin/dev artisan optimize:clear   # Clear all caches
```

## Docker Troubleshooting

```bash
# Container status
docker ps                          # Running containers
docker ps -a                       # All containers

# Container logs
docker logs laravel-perf-nginx     # Nginx logs
docker logs laravel-perf-mysql     # MySQL logs
docker logs laravel-perf-php-fpm   # PHP-FPM logs

# Container access
docker exec -it laravel-perf-php-fpm bash    # Direct container access
docker exec -it laravel-perf-mysql bash      # MySQL container

# Resource usage
docker stats                       # Container resource usage

# Network debugging
docker network ls                  # List networks
docker network inspect laravel-perf_laravel-perf  # Network details
```

## File Permissions (Linux/macOS)

```bash
# Fix Laravel permissions
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R $USER:www-data storage bootstrap/cache

# Docker permissions
sudo usermod -aG docker $USER      # Add user to docker group (logout/login required)
```

## Quick Fixes

```bash
# Application not loading
./bin/stack restart traditional
./bin/dev artisan config:clear
./bin/dev artisan cache:clear

# Database issues
./bin/dev artisan migrate:fresh --seed
./bin/stack restart traditional

# Frontend not updating
./bin/dev npm run build
# Or for development:
./bin/dev npm run dev

# Container issues
./bin/stack clean
./bin/stack up traditional -d

# Permission denied errors
chmod +x bin/dev bin/stack
```

## Environment Files

```bash
# Copy environment file
cp .env.example .env

# Generate app key
./bin/dev artisan key:generate

# Important .env variables
APP_DEBUG=true                     # Development only
DB_HOST=mysql                      # Docker service name
REDIS_HOST=redis                   # Docker service name
CACHE_STORE=redis                  # Use Redis for caching
SESSION_DRIVER=redis               # Use Redis for sessions
```

## Production Commands (for reference)

```bash
# Optimize for production
./bin/dev artisan optimize
./bin/dev npm run build

# Set production environment
# In .env:
APP_ENV=production
APP_DEBUG=false

# Clear development caches
./bin/dev artisan optimize:clear
```

## Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Project aliases
alias cda='cd /path/to/customer-dashboard'
alias dev='./bin/dev'
alias stack='./bin/stack'

# Common commands
alias art='./bin/dev artisan'
alias pf='./bin/dev artisan migrate:fresh'
alias pfs='./bin/dev artisan migrate:fresh --seed'
```

## Help Commands

```bash
./bin/dev help                     # Dev helper commands
./bin/stack help                   # Stack management help
./bin/dev artisan                  # List Artisan commands
./bin/dev artisan help migrate     # Help for specific command
```

## Common Workflows

### Starting Development Session

```bash
./bin/stack up traditional -d
./bin/dev npm run dev              # In separate terminal
# Start coding!
```

### Switching to Feature Branch

```bash
git checkout feature/repository-pattern
./bin/dev artisan migrate:fresh --seed
./bin/dev composer install
./bin/dev npm install && ./bin/dev npm run build
```

### Running Tests Before Commit

```bash
./bin/dev artisan test
./bin/dev npm run type-check
```

### Cleaning Up After Development

```bash
./bin/stack down traditional       # Or stop-all
```

This reference should cover 90% of your daily development needs!