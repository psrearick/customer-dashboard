# Docker Stacks

This project uses multiple Docker configurations (called "stacks") to demonstrate different server technologies and
optimization techniques. Each stack provides a different environment for running the same Laravel application.

## What Are Stacks?

A "stack" is a combination of containers that work together to run the application. Instead of one fixed setup, this
project lets you choose between different server configurations to explore various deployment strategies and performance
characteristics.

### Why Multiple Stacks?

Different blog posts explore different server technologies:

- Comparing traditional PHP-FPM vs. modern alternatives
- Demonstrating performance optimizations across different environments
- Testing how applications behave with different server configurations
- Providing realistic examples for production decision-making

## Available Stacks

### Traditional Stack

```bash
./bin/stack up traditional -d
```

**What it includes:** Nginx + PHP-FPM + MySQL + Redis  
**Access:** http://localhost  
**Best for:** First-time setup, most blog posts, general development

This is the most common production setup you'll find in the Laravel ecosystem. Uses Nginx as a web server with PHP-FPM
handling PHP processing.

### FrankenPHP Stack

```bash
./bin/stack up frankenphp -d
```

**What it includes:** FrankenPHP + MySQL + Redis  
**Access:** http://localhost:8080  
**Best for:** Exploring modern PHP server technology, HTTP/3 features

FrankenPHP is a modern PHP server that includes HTTP/3 support, worker mode for better performance, and automatic HTTPS.
It's built on top of the Caddy web server.

### Octane Stack

```bash
./bin/stack up octane -d
```

**What it includes:** Laravel Octane + Swoole + MySQL + Redis  
**Access:** http://localhost:8000  
**Best for:** High-performance scenarios, testing long-running processes

Laravel Octane keeps your application loaded in memory between requests, eliminating the bootstrap overhead. Uses Swoole
for async processing and improved performance.

### Performance Stack

```bash
./bin/stack up performance -d
```

**What it includes:** Traditional stack + monitoring tools  
**Access:** http://localhost (app), http://localhost:3000 (monitoring)  
**Best for:** Performance testing, optimization blog posts, detailed metrics

Adds comprehensive monitoring with Grafana dashboards, Prometheus metrics, and other performance analysis tools.

## Which Stack Should I Use?

### First Time Visitors

Start with **traditional** - it's the most straightforward and widely used setup.

### Following a Specific Blog Post

Use whatever stack the blog post mentions. Most posts will specify which stack to use for the best demonstration of the
concepts being discussed.

### Performance Testing or Comparison

Use the **performance** stack to access monitoring tools and detailed metrics.

### Exploring Modern PHP Technologies

Try **frankenphp** for HTTP/3 and modern server features, or **octane** for high-performance scenarios.

### Just Exploring the Application

**Traditional** stack is fine for browsing the application and understanding the codebase.

## Switching Between Stacks

You can only run one stack at a time. To switch:

```bash
# Stop current stack
./bin/stack down traditional

# Start different stack
./bin/stack up octane -d
```

### What Changes Between Stacks

- **URL/Port:** Different stacks use different ports
- **Performance characteristics:** Response times and resource usage vary
- **Available features:** Some stacks include monitoring tools
- **Server technology:** Different underlying web servers and PHP handlers

The Laravel application code remains the same - only the server environment changes.

## Performance Monitoring

### When Available

Monitoring tools are included with the **performance** stack and provide access to:

- **Grafana Dashboards:** http://localhost:3000 (login: admin/admin)
- **Prometheus Metrics:** http://localhost:9090
- **Application performance metrics, database queries, cache hit rates**

### What You Can Monitor

- Response times across different endpoints
- Database query performance and slow query detection
- Memory usage and resource consumption
- Cache effectiveness and hit/miss ratios
- Request volume and error rates

### Using Monitoring for Blog Posts

If you're following a performance-related blog post, the monitoring tools let you see the actual impact of optimizations
in real-time graphs and metrics.

## Stack Commands Quick Reference

### Starting and Stopping

```bash
# Start a stack in background
./bin/stack up [stack-name] -d

# Stop a specific stack
./bin/stack down [stack-name]

# Restart a stack
./bin/stack restart [stack-name]
```

### Checking Status

```bash
# See what's currently running
./bin/stack status

# View logs for troubleshooting
./bin/stack logs [stack-name]

# Follow logs in real-time
./bin/stack logs [stack-name] -f
```

### Maintenance

```bash
# Stop everything
./bin/stack stop-all

# Complete cleanup (removes all data)
./bin/stack clean
```

## Resource Requirements

### Traditional/FrankenPHP/Octane

- **RAM:** 4GB minimum
- **CPU:** 2+ cores
- **Disk:** 5GB

### Performance Stack

- **RAM:** 6GB minimum (8GB recommended)
- **CPU:** 4+ cores
- **Disk:** 10GB

### Tips for Resource Management

- Use **traditional** stack for daily development
- Only use **performance** stack when you need monitoring
- Stop stacks when not in use: `./bin/stack down [stack-name]`
- If your system is slow, try reducing Docker's resource allocation and using only the traditional stack

## Troubleshooting Stack Issues

### Stack Won't Start

- Check if ports are already in use (see [troubleshooting.md](troubleshooting.md))
- Ensure Docker has sufficient memory allocated
- Try stopping all stacks first: `./bin/stack stop-all`

### Different Behavior Between Stacks

This is expected! Each stack has different performance characteristics. If you notice differences in response times or
behavior, that's often the point of the demonstration.

### Can't Access Application on Different Ports

Double-check the port for each stack:

- Traditional: port 80 (http://localhost)
- FrankenPHP: port 8080 (http://localhost:8080)
- Octane: port 8000 (http://localhost:8000)

The choice of stack depends on what you're trying to learn or demonstrate. Most of the time, the traditional stack is
the right choice for getting started.