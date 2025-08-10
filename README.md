# Customer Dashboard - Laravel Learning & Reference Project

A real-world Laravel application designed as a teaching tool and reference implementation for my Laravel blog. This
project demonstrates various Laravel techniques, patterns, and best practices through practical examples that readers
can explore and learn from.

## Why This Project Exists

This project serves three main purposes:

1. **Blog Companion**: Provides working code examples for Laravel tutorials and articles
2. **Learning Platform**: Each git branch demonstrates a specific technique or pattern
3. **Reference Implementation**: A maintained, real-world Laravel application using current best practices

## Quick Start

```bash
# Clone the repository
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard

# Start the development environment
./bin/stack up traditional -d

# Install dependencies and set up the application
./bin/dev composer install
./bin/dev artisan key:generate
./bin/dev artisan migrate --seed
./bin/dev npm install
./bin/dev npm run build

# Visit your application
open http://localhost
```

## Learning Branches

Different branches demonstrate different Laravel techniques:

| Branch                             | Topic                                       | Blog Post     |
|------------------------------------|---------------------------------------------|---------------|
| `main`                             | Base application with React 19 + Inertia.js | [Coming Soon] |
| `feature/performance-optimization` | Performance tuning techniques               | [Coming Soon] |

To explore a specific technique:

```bash
git checkout feature/repository-pattern
./bin/dev artisan migrate:fresh --seed
```

## Documentation

- **[Getting Started](docs/getting-started.md)** - Setup instructions and first steps
- **[Tutorials](docs/tutorials/)** - Step-by-step guides for each technique
- **[Architecture Decisions](docs/architecture/)** - Why things are built this way
- **[Branch Guide](docs/branches/branch-guide.md)** - What each branch demonstrates
- **[Command Reference](docs/reference/commands.md)** - Quick command lookup
- **[Troubleshooting](docs/reference/troubleshooting.md)** - Common issues and solutions

## Technology Stack

- **Laravel 12** - Latest Laravel framework
- **React 19** - Modern frontend with Inertia.js
- **MySQL 8.4** - Primary database
- **Redis 8** - Caching and sessions
- **Docker** - Consistent development environment

## Development Environment

The project includes Docker configurations for different scenarios:

- **Traditional** (`./bin/stack up traditional -d`) - Standard Nginx + PHP-FPM setup
- **Modern** (`./bin/stack up frankenphp -d`) - FrankenPHP with HTTP/3 support
- **High-Performance** (`./bin/stack up octane -d`) - Laravel Octane with Swoole

For most development, the traditional stack is recommended. See [Docker Setup Guide](docs/architecture/docker-setup.md)
for details.

## Key Features Demonstrated

### Current Implementation (main branch)

- Laravel 12 with React 19 and Inertia.js
- Modern frontend with Radix UI components
- Docker-based development environment
- Database migrations and seeders
- Asset compilation with Vite

### Planned Examples (future branches)

- Repository and Service patterns
- API development with resources
- Testing strategies (Unit, Feature, Browser)
- Performance optimization techniques
- Authentication and authorization
- Background job processing
- Real-time features with WebSockets
- Multi-tenancy implementations

## Development Commands

```bash
# Common development tasks
./bin/dev artisan migrate        # Run migrations
./bin/dev artisan tinker         # Interactive shell
./bin/dev composer test          # Run tests
./bin/dev npm run dev           # Start Vite dev server

# View available commands
./bin/dev help
./bin/stack help
```

## For Blog Readers

If you're following along with a tutorial:

1. Check out the relevant branch mentioned in the blog post
2. Run `./bin/dev artisan migrate:fresh --seed` to reset the database
3. Follow the tutorial steps
4. Compare your implementation with the branch code

## Contributing

Contributions are welcome! If you have a Laravel technique you'd like to see demonstrated:

1. Open an issue describing the technique
2. Fork and create a feature branch
3. Implement the example with clear, educational code
4. Add documentation explaining the approach
5. Submit a pull request

## License

This project is open-sourced software licensed under the [MIT license](LICENSE).

## About

This project is maintained by Phillip Rearick as a companion to Laravel blog posts and tutorials. It serves as a living
reference implementation that evolves with Laravel best practices.

**Blog**: [philliprearick.com](https://philliprearick.com/)  
**Issues**: [GitHub Issues](https://github.com/psrearick/customer-dashboard/issues)