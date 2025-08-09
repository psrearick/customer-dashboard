# Performance Monitoring Guide

The Laravel Performance Testing Environment includes comprehensive monitoring and profiling tools to analyze application
performance, identify bottlenecks, and measure optimization improvements.

## Monitoring Stack Overview

The monitoring infrastructure consists of:

- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **ELK Stack** - Log aggregation and analysis
- **Jaeger** - Distributed tracing
- **Database Exporters** - MySQL and Redis metrics
- **XHProf** - PHP function profiling

## Grafana Dashboards

### Access Information

- **URL**: http://localhost:3000
- **Username**: `admin`
- **Password**: `admin`
- **Default Dashboard**: Laravel Performance Overview

### Pre-configured Dashboards

#### Laravel Performance Overview

**Location**: `docker/grafana/dashboards/laravel/performance-overview.json`

**Key Metrics:**

- HTTP request rate and response times
- PHP-FPM process utilization
- Memory usage patterns
- Database query performance
- Cache hit/miss ratios
- Error rates and status codes

#### System Performance Monitoring

- CPU and memory utilization
- Disk I/O and network traffic
- Container resource usage
- Service health status

### Custom Metrics

Add custom application metrics using Prometheus PHP client:

```php
use Prometheus\CollectorRegistry;
use Prometheus\Storage\Redis;

// Initialize Prometheus in Laravel
$adapter = new Redis(['host' => 'redis']);
$registry = new CollectorRegistry($adapter);

// Create custom counter
$counter = $registry->getOrRegisterCounter(
    'laravel',
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
);

$counter->incBy(1, ['GET', '/api/users', '200']);
```

## Prometheus Metrics

### Access Information

- **URL**: http://localhost:9090
- **Config**: `docker/prometheus/prometheus.yml`

### Available Metrics

#### Application Metrics

- `laravel_request_duration_seconds` - HTTP request latency
- `laravel_request_total` - Total HTTP requests
- `laravel_queue_jobs_total` - Queue job metrics
- `laravel_cache_operations_total` - Cache operations

#### Infrastructure Metrics

- `mysql_up` - MySQL server availability
- `redis_up` - Redis server availability
- `nginx_requests_total` - Nginx request metrics
- `php_fpm_processes` - PHP-FPM process counts

#### Database Metrics (via mysql-exporter)

- `mysql_global_status_queries` - Query execution rate
- `mysql_global_status_slow_queries` - Slow query count
- `mysql_innodb_buffer_pool_pages_data` - Buffer pool utilization
- `mysql_info_schema_query_response_time` - Query response times

#### Cache Metrics (via redis-exporter)

- `redis_commands_processed_total` - Command execution rate
- `redis_memory_used_bytes` - Memory utilization
- `redis_connected_clients` - Active connections
- `redis_keyspace_hits_total` / `redis_keyspace_misses_total` - Hit ratio

### Custom Recording Rules

**Location**: `docker/prometheus/recording_rules.yml`

```yaml
groups:
  - name: laravel_performance
    interval: 30s
    rules:
      - record: laravel:request_rate_5m
        expr: rate(laravel_request_total[5m])

      - record: laravel:error_rate_5m
        expr: rate(laravel_request_total{status=~"5.."}[5m])

      - record: laravel:response_time_p95_5m
        expr: histogram_quantile(0.95, rate(laravel_request_duration_seconds_bucket[5m]))
```

### Alerting Rules

**Location**: `docker/prometheus/alert_rules.yml`

```yaml
groups:
  - name: laravel_alerts
    rules:
      - alert: HighResponseTime
        expr: laravel:response_time_p95_5m > 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: High response time detected

      - alert: DatabaseDown
        expr: mysql_up == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: MySQL database is down
```

## ELK Stack (Elasticsearch + Kibana)

### Access Information

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

### Log Analysis Features

#### Application Logs

- Laravel application logs via JSON format
- PHP error logs and stack traces
- Web server access logs
- Database slow query logs

#### Performance Analysis

- Request/response log correlation
- Error pattern identification
- Performance trend analysis
- User behavior tracking

### Kibana Dashboards

#### Laravel Application Dashboard

- Request volume and patterns
- Error rates by endpoint
- Response time distributions
- User session analysis

#### Infrastructure Dashboard

- Container health monitoring
- Resource utilization trends
- Service dependency mapping
- Alert correlation

### Custom Log Parsing

Configure structured logging in Laravel:

```php
// config/logging.php
'channels' => [
    'elasticsearch' => [
        'driver' => 'custom',
        'via' => ElasticsearchLogger::class,
        'formatter' => 'json',
        'formatter_with' => [
            'includeStacktraces' => true,
            'service' => 'laravel-app',
            'environment' => env('APP_ENV'),
        ],
    ],
],
```

## Distributed Tracing (Jaeger)

### Access Information

- **URL**: http://localhost:16686
- **Protocol**: Zipkin compatible

### Tracing Capabilities

#### Request Flow Visualization

- End-to-end request tracing
- Service dependency mapping
- Performance bottleneck identification
- Error propagation tracking

#### Integration with Laravel

```php
use OpenTracing\GlobalTracer;
use Jaeger\Config;

// Initialize Jaeger tracer
$config = new Config(
    [
        'sampler' => ['type' => 'const', 'param' => 1],
        'logging' => true,
    ],
    'laravel-app'
);
$tracer = $config->initializeTracer();
GlobalTracer::set($tracer);

// Create spans in controllers
public function index()
{
    $span = GlobalTracer::get()->startSpan('user.index');
    
    // Your controller logic
    $users = User::all();
    
    $span->setTag('user.count', $users->count());
    $span->finish();
    
    return response()->json($users);
}
```

## PHP Profiling (XHProf)

### Integration Setup

**Container**: Custom XHProf container with web interface  
**Access**: http://localhost:8080 (when XHProf stack is running)

### Profiling Configuration

Enable XHProf in specific environments:

```php
// Enable profiling for specific requests
if (isset($_GET['profile']) || env('XHPROF_ENABLED', false)) {
    xhprof_enable(XHPROF_FLAGS_MEMORY | XHPROF_FLAGS_CPU);
}

// Save profiling data
register_shutdown_function(function() {
    if (function_exists('xhprof_disable')) {
        $data = xhprof_disable();
        $runs = new XHProfRuns_Default();
        $runId = $runs->save_run($data, 'laravel');
        
        // Log the profile URL
        Log::info("XHProf profile: http://localhost:8080/xhprof_html/index.php?run={$runId}&source=laravel");
    }
});
```

### Performance Analysis Features

- Function-level execution time
- Memory allocation tracking
- Call graph visualization
- Comparison between runs
- Bottleneck identification

## Performance Metrics Collection

### Key Performance Indicators (KPIs)

#### Response Time Metrics

- **P50 (Median)**: 50th percentile response time
- **P95**: 95th percentile response time
- **P99**: 99th percentile response time
- **Average**: Mean response time

#### Throughput Metrics

- **Requests per second (RPS)**
- **Concurrent users supported**
- **Peak load capacity**
- **Queue processing rate**

#### Resource Utilization

- **CPU usage percentage**
- **Memory consumption**
- **Database connection pool**
- **Cache hit ratio**

#### Error Metrics

- **Error rate percentage**
- **5xx server errors**
- **Database connection failures**
- **Cache miss ratio**

### Baseline Measurement

Before optimization, establish baselines:

```bash
# Start performance stack
./stack.sh up performance -d

# Run baseline load test
artillery run docker/artillery/load-test-config.yml

# Capture metrics in Grafana
# Document current performance numbers
```

### A/B Testing Framework

Compare different configurations:

```bash
# Test traditional stack
./stack.sh up traditional -d
artillery run docker/artillery/load-test-config.yml > traditional-results.txt

# Test FrankenPHP stack  
./stack.sh down traditional
./stack.sh up frankenphp -d
artillery run docker/artillery/load-test-config.yml > frankenphp-results.txt

# Test Octane stack
./stack.sh down frankenphp
./stack.sh up octane -d
artillery run docker/artillery/load-test-config.yml > octane-results.txt
```

## Performance Testing Scenarios

### Load Testing with Artillery

**Configuration**: `docker/artillery/load-test-config.yml`

```yaml
config:
  target: 'http://nginx'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 50
    - duration: 60
      arrivalRate: 100

scenarios:
  - name: "User workflow"
    weight: 100
    flow:
      - get:
          url: "/"
      - think: 2
      - get:
          url: "/api/users"
      - think: 1
      - post:
          url: "/api/users"
          json:
            name: "Test User"
            email: "test@example.com"
```

### Continuous Performance Monitoring

Set up automated performance regression detection:

```bash
#!/bin/bash
# performance-check.sh

# Run load test and capture metrics
BASELINE_P95=$(curl -s 'http://localhost:9090/api/v1/query?query=laravel:response_time_p95_5m' | jq -r '.data.result[0].value[1]')

# Compare with threshold
if (( $(echo "$BASELINE_P95 > 0.5" | bc -l) )); then
    echo "⚠️  Performance regression detected: P95 = ${BASELINE_P95}s"
    exit 1
else
    echo "✅ Performance within acceptable limits: P95 = ${BASELINE_P95}s"
fi
```

## Monitoring Configuration

### Prometheus Configuration

**File**: `docker/prometheus/prometheus.yml`

Key scrape targets:

- Laravel application metrics
- MySQL exporter metrics
- Redis exporter metrics
- Nginx metrics (via stub_status)
- Container metrics (cAdvisor)

### Grafana Data Sources

**File**: `docker/grafana/datasources/datasources.yml`

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true

  - name: Elasticsearch
    type: elasticsearch
    url: http://elasticsearch:9200
    access: proxy
    database: logstash-*
    interval: Daily
```

### Alert Manager Integration

Configure Slack/email notifications for performance alerts:

```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

route:
  group_by: [ 'alertname' ]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    slack_configs:
      - channel: '#performance-alerts'
        title: 'Performance Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

This comprehensive monitoring setup provides deep insights into Laravel application performance and enables data-driven
optimization decisions.