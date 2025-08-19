# Getting Started

This guide will help you set up and run the customer management SaaS application locally. If you're here from a blog
post, this will get you up and running with the specific code examples discussed.

## Prerequisites

Before you begin, make sure you have:

- **Docker Desktop** 4.0+ with at least 4GB RAM allocated
- **Git** for cloning the repository and switching branches
- **8GB+ system RAM** (some stacks require significant resources)
- **10GB+ free disk space** for containers and data

### Docker Setup

If you haven't used Docker before:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Start Docker Desktop and ensure it's running
3. Increase memory allocation: Docker Desktop → Settings → Resources → Memory → 4GB+

## Quick Setup

### 1. Clone and Enter the Repository

```bash
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard
```

### 2. Set Up Environment

```bash
# Copy the environment configuration
cp .env.example .env
```

### 3. Start the Application

```bash
# Start the default Docker stack (no -s option needed for default)
./bin/app stack up

# Generate application key
./bin/dev artisan key:generate

# Install dependencies
./bin/dev composer install

# Set up the database with sample data
./bin/dev artisan migrate --seed

# Install and build frontend assets
./bin/dev npm install
./bin/dev npm run build
```

### 4. Access the Application

Open your browser and go to: **http://localhost**

You should see the customer dashboard with sample data including customers, orders, and activity tracking.

## Understanding the Application

### What You're Looking At

This is a multi-tenant customer management SaaS application that includes:

- **Customer Management** - Customer profiles and account information
- **Order Processing** - Orders with line items and product relationships
- **Activity Tracking** - User actions and system events
- **Notifications** - Alert system for various events
- **Multi-tenancy** - Data isolation between different customer accounts

### Sample Data

The seeded database includes:

- Multiple tenant accounts with realistic data distributions
- Customers with associated orders and activities
- Product catalog with categories and pricing
- User accounts with different permission levels

### Key Sections

- **Dashboard** - Overview of key metrics and recent activity
- **Customers** - Customer list and detailed profiles
- **Orders** - Order management and tracking
- **Products** - Product catalog and inventory
- **Reports** - Analytics and performance metrics

## Docker Stacks

This project includes multiple server configurations to demonstrate different deployment strategies:

### Why Multiple Stacks?

Different blog posts explore different server technologies and optimization techniques. Each stack provides a different
environment for testing and comparison.

### Available Stacks

- **Default** (`./bin/app stack up` or `./bin/app stack up -s default`) - Standard Nginx + PHP-FPM setup
  - This is the default stack used when no `-s` option is provided
- **FrankenPHP** (`./bin/app stack up -s frankenphp`) - Modern HTTP/3 server, accessible at http://localhost:8080
- **Octane** (`./bin/app stack up -s octane`) - High-performance Laravel Octane, accessible at http://localhost:8000

### Which Stack to Use

- **First time visitors:** Start with default (just use `./bin/app stack up` without any options)
- **Following a blog post:** Use the stack mentioned in the post
- **Exploring modern PHP:** Try `frankenphp` or `octane`

### Switching Stacks

```bash
# Stop current stack (stops default if no -s specified)
./bin/app stack stop

# Start different stack (must specify -s for non-default stacks)
./bin/app stack up -s octane
```

## Working with Blog Post Branches

### Switching to a Blog Post Branch

If you're following a specific blog post, switch to the corresponding branch:

```bash
# Example: switch to a performance optimization branch
git checkout demo/performance/query-optimized

# After switching, update dependencies and database
./bin/dev composer install
./bin/dev artisan migrate:fresh --seed
./bin/dev npm install && ./bin/dev npm run build
```

### Branch Naming Convention

Blog post branches follow this pattern:

- `demo/performance/*` - Performance optimization examples
- `demo/architecture/*` - Architectural pattern demonstrations
- `demo/ai/*` - AI/ML integration examples

### Cleaning Up

To reset everything to a clean state:

```bash
# Complete reset
./bin/app stack clean
git checkout main
./bin/app stack up
# Run setup steps again
```

## Verifying Everything Works

### Application Access

- **Main Application:** http://localhost (default stack)
- **FrankenPHP:** http://localhost:8080
- **Octane:** http://localhost:8000

### What You Should See

1. A functional dashboard with sample data
2. Navigation between customers, orders, and products
3. Realistic data relationships and interactions

### Basic Functionality Test

1. Browse the customer list
2. View a customer's order history
3. Check the dashboard metrics
4. Navigate between different sections

### Monitoring Tools (Performance Stack)

If using the performance stack, you can also access:

- **Grafana Dashboard:** http://localhost:3000 (admin/admin)
- **Prometheus Metrics:** http://localhost:9090

## Helper Commands

The project includes several utility scripts to make common tasks easier:

### Quick Setup

```bash
# Complete setup in one command
./bin/setup
```

This handles the entire initial setup: copies environment files, starts Docker containers, installs dependencies, sets
up the database, and builds frontend assets. Perfect for first-time setup or when following a blog post link.

### Reset Application

```bash
# Reset database and dependencies after switching branches
./bin/reset
```

Use this after switching to a different branch or when you need a clean slate. Resets the database with fresh seed data,
reinstalls dependencies, and rebuilds assets.

### Switch to Blog Post Branch

```bash
# Switch to a specific branch and reset everything
./bin/branch demo/performance/query-optimized
```

Combines `git checkout` with a complete application reset. This is the easiest way to switch between different blog post
demonstrations.

### When to Use Each Command

- **First time setup:** `./bin/setup`
- **Following a blog post:** `./bin/branch <branch-name>`
- **Things seem broken:** `./bin/reset`
- **Switched branches manually:** `./bin/reset`

These commands handle all the repetitive tasks so you can focus on exploring the code and concepts discussed in the blog
posts.

## Next Steps

### If Something's Not Working

Check the [troubleshooting guide](troubleshooting.md) for common issues and solutions.

### Exploring the Code

- Review the Laravel application structure in standard directories (`app/`, `routes/`, `resources/`)
- Check out the Docker configuration in `docker/` directory
- Look at database migrations in `database/migrations/` to understand the data model

### Blog Post Context

Each blog post will reference specific files, classes, or techniques demonstrated in the codebase. Use this running
application as a reference while reading to see the concepts in action.

### Getting Help

- **Common Issues:** See [troubleshooting.md](troubleshooting.md)
- **Docker Problems:** See [docker-stacks.md](docker-stacks.md)
- **Application Issues:** Check container logs with `./bin/app stack logs`

The application should now be running and ready for you to explore the concepts discussed in the blog posts.