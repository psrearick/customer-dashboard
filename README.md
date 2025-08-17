# Customer Dashboard Demo Application

## Introduction

This is a multi-tenant customer management SaaS application that serves as a demonstration platform for Laravel
optimization techniques and architectural patterns. It supports the content
of [Phillip Rearick's blog](https://philliprearick.com), providing working code examples for the concepts discussed.

While code snippets and explanations are helpful, sometimes you only understand something after seeing it in practice.
This project goes beyond basic examples by demonstrating techniques in the context of a complete application with
realistic complexity, with features such as managing customers, orders, products, and activity tracking across multiple tenants.

## What You'll Find Here

### The Application

A customer management platform with:

- Multi-tenant architecture with data isolation
- Customer profiles and order management
- Product catalog and inventory tracking
- Activity monitoring and notifications
- Real-world complexity suitable for optimization demonstrations

### Blog Post Demonstrations

Different branches showcase specific techniques:

- **Performance optimizations** - Query improvements, caching strategies, memory management
- **Architectural patterns** - Domain-driven design, event sourcing, hexagonal architecture
- **Modern integrations** - AI features, real-time capabilities, advanced Laravel patterns

## Quick Start

```bash
# Clone the repository
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard

# Complete setup in one command
./bin/setup

# Access the application
open http://localhost
```

## Following Blog Posts

If you're here from a specific blog post, you can jump directly to the relevant code:

```bash
# Switch to a blog post branch (example)
./bin/branch demo/performance/query-optimized
```

Many blog posts link to specific branches that demonstrate the techniques being discussed. If the branch you're on has
an associated blog post, look for [README.blog.md](README.blog.md) for post-specific instructions.

## Exploring Different Server Technologies

The project includes multiple Docker configurations to compare different deployment strategies:

```bash
# Default: Nginx + PHP-FPM (default)
./bin/app up -s default

# Modern: FrankenPHP with HTTP/3
./bin/app up -s frankenphp

# High-performance: Laravel Octane  
./bin/app up -s octane
```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Detailed setup and usage guide
- **[Docker Stacks](docs/docker-stacks.md)** - Understanding the different server configurations
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## Getting Help

If you have questions or run into issues:

- Check the [troubleshooting guide](docs/troubleshooting.md) for common problems
- [Create an issue on GitHub](https://github.com/psrearick/customer-dashboard/issues) for bugs or questions
- Review the documentation in the `docs/` directory

## Contributing

Please see [CONTRIBUTING](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is open-sourced software licensed under the [MIT license](LICENSE).
