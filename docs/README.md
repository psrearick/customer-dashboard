# Laravel Performance Testing Environment - Documentation

Welcome to the comprehensive documentation for the Laravel Performance Testing Environment. This documentation provides
everything you need to understand, set up, and use this powerful Docker-based testing platform.

## Documentation Structure

### Getting Started

- **[Getting Started Guide](getting-started.md)** - Setup instructions and first steps
- **[Stack Management](stack-management.md)** - Available stacks and management commands

### Reference Documentation

- **[Container Reference](containers.md)** - Complete container and service documentation
- **[Configuration Guide](configuration.md)** - Configuration file structures and examples
- **[Configuration Reference](configuration-reference.md)** - Comprehensive configuration tuning guide
- **[Performance Monitoring](monitoring.md)** - Monitoring and profiling tools

### Support

- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Quick Navigation

### New Users

1. Start with [Getting Started Guide](getting-started.md)
2. Learn about [Stack Management](stack-management.md)
3. Explore [Performance Monitoring](monitoring.md)

### Advanced Users

1. Review [Container Reference](containers.md) for technical details
2. Customize with [Configuration Guide](configuration.md)
3. Debug issues using [Troubleshooting](troubleshooting.md)

### Developers & Contributors

1. Understand the architecture in [Container Reference](containers.md)
2. Extend configurations using [Configuration Guide](configuration.md)
3. Add monitoring with [Performance Monitoring](monitoring.md)

## Environment Overview

The Laravel Performance Testing Environment provides:

### **Multiple Web Server Configurations**

- **Traditional**: Nginx + PHP-FPM (industry standard)
- **Modern**: FrankenPHP with HTTP/3 and worker mode
- **High-Performance**: Laravel Octane with Swoole

### **Comprehensive Database Stack**

- **MySQL 8.4**: Primary database with performance tuning
- **Redis 8**: High-performance caching with clustering
- **Multi-tenant**: Separate database instances for isolation testing
- **Proxies**: ProxySQL and PgBouncer for connection management

### **Advanced Monitoring & Profiling**

- **Prometheus + Grafana**: Metrics collection and visualization
- **ELK Stack**: Elasticsearch + Kibana for log analysis
- **Jaeger**: Distributed tracing for request analysis
- **XHProf**: Detailed PHP function profiling
- **Database Exporters**: MySQL and Redis specific metrics

### **Performance Analysis Tools**

- **Percona Toolkit**: MySQL query analysis and optimization
- **Load Testing**: Artillery integration for performance testing
- **Health Monitoring**: Comprehensive service health checks
- **Resource Monitoring**: Container and system resource tracking

## Architecture Highlights

### Container Architecture

- **25+ specialized containers** for different testing scenarios
- **7 docker-compose files** for flexible stack combinations
- **External networking** for service discovery and communication
- **Persistent volumes** for data retention and performance

### Performance Features

- **HTTP/3 Support** via FrankenPHP for next-generation web performance
- **Worker Mode** for eliminating PHP bootstrap overhead
- **Connection Pooling** for efficient database resource utilization
- **Distributed Caching** with Redis clustering
- **JIT Compilation** with PHP 8.4 OPcache optimization

### Monitoring Capabilities

- **Real-time Metrics** with sub-second granularity
- **Custom Dashboards** for Laravel-specific performance indicators
- **Alerting Rules** for proactive performance monitoring
- **Log Aggregation** for comprehensive error tracking and analysis

## Quick Reference

### Essential Commands

```bash
# Start traditional stack
./stack.sh up traditional -d

# Monitor performance  
./stack.sh up performance -d

# Compare all servers
./stack.sh up comparison -d

# Check status
./stack.sh status

# View logs
./stack.sh logs [stack] -f
```

### Key URLs (when running)

- **Application**: http://localhost (varies by stack)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Jaeger**: http://localhost:16686

### Port Allocation

- **80**: Nginx (traditional)
- **8080**: FrankenPHP
- **8000**: Laravel Octane
- **8090**: Load Balancer
- **3306-3308**: MySQL instances
- **6379, 7010-7012**: Redis instances

## Documentation Features

### Comprehensive Coverage

- **Step-by-step instructions** for all procedures
- **Code examples** for integration and customization
- **Troubleshooting scenarios** with specific solutions
- **Performance optimization** guidelines and best practices

### Technical Depth

- **Container specifications** including images, ports, and volumes
- **Configuration file documentation** with all available options
- **Monitoring setup instructions** for comprehensive observability
- **Extension mechanisms** for customizing the environment

### Practical Focus

- **Real-world examples** based on actual Laravel applications
- **Performance testing workflows** for systematic optimization
- **Benchmarking methodologies** for reliable comparisons
- **Production considerations** for scaling and deployment

## Contributing to Documentation

We welcome documentation improvements! When contributing:

1. **Follow the established structure** outlined in each document
2. **Include practical examples** for all concepts
3. **Test all procedures** before documenting them
4. **Update cross-references** when adding new content
5. **Maintain consistency** in formatting and terminology

### Documentation Standards

- Use clear, concise language suitable for all skill levels
- Include command examples with expected outputs
- Provide troubleshooting information for common issues
- Link to relevant sections in other documents
- Update the documentation index when adding new content

## Getting Help

If you need assistance:

1. **Check the appropriate documentation section** for your topic
2. **Review the troubleshooting guide** for common solutions
3. **Search existing issues** in the GitHub repository
4. **Create a detailed issue report** with system information and logs
5. **Join the community discussions** for peer support

The documentation is designed to be self-sufficient, but we're committed to helping users succeed with the Laravel
Performance Testing Environment.
