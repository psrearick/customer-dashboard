# Configuration Guide

This guide explains the configuration philosophy and key settings without duplicating the actual configuration files.
For specific settings, refer to the actual files in the `docker/` directory.

## Configuration Philosophy

1. **Development First**: Default settings optimized for learning and debugging
2. **Progressive Complexity**: Start simple, add configuration as needed
3. **Documentation Over Duplication**: Reference files, don't copy them
4. **Environment-Specific**: Different settings for development vs. production

## Key Configuration Files

### PHP Configuration

**Location**: `docker/php/conf.d/`

#### Development Settings (`performance.ini`)

**File**: [`docker/php/conf.d/performance.ini`](../../docker/php/conf.d/performance.ini)

**Key Decisions**:

- `memory_limit = 512M`: Generous limit for development debugging
- `max_execution_time = 300`: Long timeout for debugging sessions
- `display_errors = On`: See errors immediately during development

**When to Modify**:

- Processing large datasets → Increase `memory_limit`
- Long-running operations → Increase `max_execution_time`
- Production deployment → Set `display_errors = Off`

#### OPcache Settings (`opcache.ini`)

**File**: [`docker/php/conf.d/opcache.ini`](../../docker/php/conf.d/opcache.ini)

**Why OPcache Matters**:

- Caches compiled PHP code in memory
- Can improve performance by 2-3x
- Critical for production performance

**Development vs Production**:

```
Development: opcache.validate_timestamps = 1  # Check for file changes
Production:  opcache.validate_timestamps = 0  # Never check (faster)
```

#### Xdebug Configuration (`xdebug.ini`)

**File**: [`docker/php/conf.d/xdebug.ini`](../../docker/php/conf.d/xdebug.ini)

**When Enabled**:

- Step debugging with IDE
- Code coverage for tests
- Profiling for performance analysis

**Performance Impact**: ~2-5x slower - disable in production!

### Web Server Configuration

#### Nginx (Traditional Stack)

**File**: [`docker/nginx/conf.d/laravel.conf`](../../docker/nginx/conf.d/laravel.conf)

**Key Patterns to Understand**:

1. **Try Files Directive**: Routes all requests through `index.php`
2. **FastCGI Settings**: How Nginx communicates with PHP
3. **Static File Caching**: Improves performance for assets
4. **Security Headers**: Protects against common attacks

**Common Modifications**:

- Increase `client_max_body_size` for file uploads
- Add custom headers for CORS
- Configure SSL certificates

#### FrankenPHP (Modern Stack)

**File**: [`docker/frankenphp/Caddyfile`](../../docker/frankenphp/Caddyfile)

**Why FrankenPHP**:

- Built-in HTTPS (automatic certificates)
- HTTP/3 support
- Worker mode (keeps app in memory)
- Simpler configuration

**When to Use**:

- Experimenting with latest technology
- Need HTTP/3 support
- Want automatic HTTPS

### Database Configuration

#### MySQL Settings

**File**: [`docker/mysql/conf.d/performance.cnf`](../../docker/mysql/conf.d/performance.cnf)

**Critical Settings Explained**:

**Buffer Pool Size**:

```
Development:  innodb_buffer_pool_size = 256M  # Conservative
Production:   innodb_buffer_pool_size = 1G+   # 70% of RAM
```

This is the #1 MySQL performance setting - it's the cache for your data.

**Connection Limits**:

```
max_connections = 200
```

Each connection uses memory. Balance between availability and resources.

**Slow Query Log**:

```
slow_query_log = 1
long_query_time = 2
```

Essential for finding performance bottlenecks.

### Laravel Configuration

#### Environment Variables (`.env`)

**Database Connection**:

```env
DB_HOST=mysql          # Docker service name
DB_DATABASE=laravel_perf
DB_USERNAME=laravel
DB_PASSWORD=password   # Change in production!
```

**Cache & Sessions**:

```env
CACHE_STORE=redis      # Fast in-memory caching
SESSION_DRIVER=redis   # Scalable session storage
QUEUE_CONNECTION=redis # Background job processing
```

**Why Redis for Everything**:

- Single source of truth for temporary data
- Extremely fast (in-memory)
- Supports advanced data structures
- Easy to scale horizontally

## Configuration by Environment

### Development Configuration

**Goals**: Fast feedback, easy debugging, file watching

**Characteristics**:

- File change detection enabled
- Verbose error reporting
- No aggressive caching
- Debug tools enabled

**Key Files to Review**:

- `.env` - Set `APP_DEBUG=true`
- `docker/php/conf.d/xdebug.ini` - Debugging enabled
- `docker/php/conf.d/opcache.ini` - File checking enabled

### Staging Configuration

**Goals**: Test production behavior, catch issues

**Characteristics**:

- Production-like settings
- Debug tools available but not enabled
- Moderate caching
- Real data volumes

**Key Changes from Development**:

- Set `APP_DEBUG=false`
- Increase cache timeouts
- Enable query caching
- Use production-like data

### Production Configuration

**Goals**: Maximum performance, security, stability

**Characteristics**:

- No file change detection
- Minimal logging
- Aggressive caching
- Security hardening

**Critical Changes**:

- `APP_DEBUG=false` and `APP_ENV=production`
- OPcache timestamps disabled
- Xdebug completely removed
- SSL/TLS required
- Rate limiting enabled

## Performance Tuning Checklist

### Application Level

- [ ] Enable OPcache
- [ ] Configure Redis caching
- [ ] Optimize autoloader: `composer dump-autoload -o`
- [ ] Cache config: `artisan config:cache`
- [ ] Cache routes: `artisan route:cache`

### Database Level

- [ ] Tune buffer pool size
- [ ] Enable slow query log
- [ ] Add appropriate indexes
- [ ] Configure connection pooling

### Web Server Level

- [ ] Enable gzip compression
- [ ] Configure static file caching
- [ ] Set appropriate worker counts
- [ ] Enable HTTP/2 or HTTP/3

## Security Configuration

### Essential Security Settings

1. **Environment Files**: Never commit `.env` to git
2. **Debug Mode**: Always `false` in production
3. **Error Display**: Hide errors from users in production
4. **HTTPS**: Required for production
5. **Headers**: Set security headers (CSP, HSTS, etc.)

### Files to Secure

- `.env` - Contains secrets
- `storage/` - May contain sensitive uploads
- `database/` - May contain seed data

## Monitoring Configuration

### What to Monitor

1. **Application Metrics**:
    - Response times
    - Error rates
    - Queue lengths

2. **System Metrics**:
    - CPU usage
    - Memory usage
    - Disk I/O

3. **Database Metrics**:
    - Query performance
    - Connection pool usage
    - Slow queries

### Configuration Files

- [`docker/prometheus/prometheus.yml`](../../docker/prometheus/prometheus.yml) - Metrics collection
- [`docker/grafana/datasources/`](../../docker/grafana/datasources/) - Dashboard configuration

## Common Configuration Patterns

### Pattern 1: Feature Flags

```env
FEATURE_NEW_DASHBOARD=true
FEATURE_API_V2=false
```

Control feature rollout without deploying code.

### Pattern 2: Service URLs

```env
EXTERNAL_API_URL=https://api.example.com
WEBHOOK_URL=https://example.com/webhook
```

Centralize external service configuration.

### Pattern 3: Rate Limits

```env
API_RATE_LIMIT=60
API_RATE_LIMIT_DECAY=1
```

Protect your application from abuse.

## Troubleshooting Configuration Issues

### Application Won't Start

1. Check `.env` exists and has all required values
2. Verify database connection settings
3. Ensure Redis is running
4. Check file permissions

### Poor Performance

1. Review OPcache settings
2. Check MySQL buffer pool size
3. Verify Redis is being used for caching
4. Look for N+1 queries

### High Memory Usage

1. Reduce PHP memory_limit
2. Decrease MySQL buffer pool
3. Check for memory leaks in code
4. Review queue worker settings

## Best Practices

1. **Version Control**: Track configuration files (not `.env`)
2. **Documentation**: Document why settings were chosen
3. **Testing**: Test configuration changes in staging first
4. **Monitoring**: Watch metrics after configuration changes
5. **Rollback Plan**: Know how to revert changes quickly

## Further Learning

Each configuration area has deeper documentation:

- PHP Configuration: [PHP.net documentation](https://www.php.net/manual/en/ini.list.php)
- MySQL Tuning: [MySQL documentation](https://dev.mysql.com/doc/)
- Nginx Configuration: [Nginx documentation](https://nginx.org/en/docs/)
- Laravel Configuration: [Laravel documentation](https://laravel.com/docs/11.x/configuration)

Remember: Don't optimize prematurely. Start with defaults, measure performance, then tune based on actual bottlenecks.