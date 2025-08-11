# Development Helper Commands

The `dev` script provides Laravel Sail-like shortcuts for running commands in Docker containers without needing to type
full `docker exec` commands.

## Installation

The `dev` script is included in the project `bin` directory and is executable. No additional installation is needed.

## Usage

```bash
dev [COMMAND] [ARGUMENTS...]
```

## Available Commands

### PHP Commands

```bash
# Run PHP commands
dev php --version
dev php script.php
```

### Laravel Artisan

```bash
# Run artisan commands
dev artisan migrate
dev artisan migrate:fresh --seed
dev artisan tinker
dev artisan queue:work
dev artisan make:controller UserController
```

### Composer

```bash
# Run composer commands
dev composer install
dev composer require package/name
dev composer update
dev composer dump-autoload
```

### NPM/Node

```bash
# Run npm commands in the Node container
dev npm install
dev npm run dev
dev npm run build
dev npm run type-check

# Run node directly
dev node --version
dev node script.js

# Note: With the dedicated Node container, Vite dev server
# starts automatically when the container launches.
# You can check its status with:
docker logs laravel-perf-node
```

### Interactive Shell

```bash
# Open a shell in the PHP container
dev shell
dev bash  # alias for shell
```

### Database Access

```bash
# Connect to MySQL as laravel user
dev mysql
# Password: password

# Connect to MySQL as root user
dev mysql-root
# Password: rootpassword

# Connect to Redis
dev redis-cli
```

## Container Auto-Detection

The script automatically detects which containers are running:

**PHP Containers:**
- **laravel-perf-php-fpm** - Used by traditional stack
- **laravel-perf-frankenphp** - Used by frankenphp stack
- **laravel-perf-octane** - Used by octane stack

**Node Container:**
- **laravel-perf-node** - Handles all frontend tooling and Vite dev server

**Important:** Node.js and npm are ONLY available in the Node container. The PHP containers do not have Node.js installed, ensuring clean separation of concerns.

You don't need to specify which container to use - the script will find the running one automatically.

## Examples

### Common Development Tasks

```bash
# Install dependencies
dev composer install
dev npm install

# Run database migrations
dev artisan migrate

# Create and seed database
dev artisan migrate:fresh --seed

# Start development server (if not auto-started)
dev npm run dev

# Build production assets
dev npm run build

# Check Node container status
docker logs laravel-perf-node

# Run tests
dev artisan test
dev php vendor/bin/phpunit

# Clear caches
dev artisan cache:clear
dev artisan config:clear
dev artisan route:clear
dev artisan view:clear

# Generate application key
dev artisan key:generate

# Create a new controller
dev artisan make:controller UserController

# Start queue worker
dev artisan queue:work

# Start Laravel Tinker
dev artisan tinker
```

### Working with Different Stacks

```bash
# Start a stack first
stack up traditional -d

# Then use dev commands
dev artisan migrate
dev npm run dev

# Switch to another stack
stack down traditional
stack up octane -d

# Dev commands still work - auto-detects new container
dev artisan octane:status
```

## Troubleshooting

### No PHP Container Running

If you see this error:

```
Error: No PHP container is running
Start a stack first with: stack up [stack] -d
```

Solution: Start a stack using the stack.sh script:

```bash
stack up traditional -d
# or
stack up frankenphp -d
# or
stack up octane -d
```

### Command Not Found

If a command is not found in the container, you may need to install it:

```bash
# Install missing npm packages
dev npm install

# Install missing composer packages
dev composer install
```

## Comparison with Laravel Sail

| Laravel Sail    | This Project    | 
|-----------------|-----------------|
| `sail php`      | `dev php`       |
| `sail artisan`  | `dev artisan`   |
| `sail composer` | `dev composer`  |
| `sail npm`      | `dev npm`       |
| `sail node`     | `dev node`      |
| `sail shell`    | `dev shell`     |
| `sail mysql`    | `dev mysql`     |
| `sail redis`    | `dev redis-cli` |

## Benefits

1. **Simplicity** - No need to remember container names or docker exec syntax
2. **Auto-detection** - Works with any running PHP container
3. **Consistency** - Same commands work regardless of which stack is running
4. **Familiarity** - Similar to Laravel Sail commands
5. **Efficiency** - Shorter commands for common tasks

## Advanced Usage

### Piping and Redirection

The dev script supports standard Unix piping and redirection:

```bash
# Pipe output
dev artisan route:list | grep api

# Redirect output to file
dev composer show > packages.txt

# Use input redirection
dev mysql < database-dump.sql
```

### Running Scripts

```bash
# Run a PHP script
dev php scripts/data-import.php

# Run a Node script  
dev node scripts/build-assets.js
```

### Interactive Commands

Interactive commands work seamlessly:

```bash
# Laravel Tinker
dev artisan tinker

# Interactive MySQL session
dev mysql

# Interactive Redis CLI
dev redis-cli
```

## Integration with Stack Management

The `dev` script works seamlessly with the `stack.sh` script:

1. Start your preferred stack: `stack up [stack] -d`
2. Use dev commands: `dev artisan migrate`
3. Switch stacks anytime - dev commands auto-adapt

See [Stack Management](stack-management.md) for more details on available stacks.