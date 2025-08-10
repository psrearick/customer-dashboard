# Customer Dashboard - Documentation

Welcome to the documentation for the Customer Dashboard project. This is a Laravel learning and reference project designed to teach modern Laravel development patterns through practical examples.

## Documentation Structure

### Getting Started
- **[Getting Started Guide](getting-started.md)** - Setup instructions and first steps
- **[Architecture Overview](architecture/overview.md)** - Why things are built this way
- **[Docker Setup](architecture/docker-setup.md)** - Understanding the development environment

### Learning Resources
- **[Tutorials](tutorials/)** - Step-by-step guides for Laravel patterns
- **[Branch Guide](branches/branch-guide.md)** - What each git branch demonstrates
- **[Frontend Development](frontend-development.md)** - React 19 + Inertia.js patterns

### Reference
- **[Command Reference](reference/commands.md)** - Quick command lookup
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions
- **[Development Commands](dev-commands.md)** - Helper script documentation

### Architecture & Configuration
- **[Configuration Guide](architecture/configuration-guide.md)** - Configuration principles
- **[Container Reference](containers.md)** - Docker service details
- **[Stack Management](stack-management.md)** - Docker stack operations

## Quick Navigation

### New to Laravel
1. Start with [Getting Started Guide](getting-started.md)
2. Understand [Architecture Decisions](architecture/overview.md)
3. Try the [Repository Pattern Tutorial](tutorials/repository-pattern.md)

### Learning Specific Patterns
1. Browse [Available Tutorials](tutorials/)
2. Check out [Branch Guide](branches/branch-guide.md) for git branches
3. Follow along with blog posts and examples

### Need Quick Help
1. [Command Reference](reference/commands.md) for common commands
2. [Troubleshooting](reference/troubleshooting.md) for common issues
3. [Docker Setup](architecture/docker-setup.md) for environment problems

### Contributing or Extending
1. Read [Architecture Overview](architecture/overview.md)
2. Review [Configuration Guide](architecture/configuration-guide.md)
3. Check [Container Reference](containers.md) for technical details

## Project Overview

The Customer Dashboard is a learning-focused Laravel project that demonstrates:

### **Modern Laravel Stack**

- **Laravel 12**: Latest framework features and best practices
- **React 19 + Inertia.js**: Modern SPA without API complexity
- **TypeScript**: Type-safe frontend development
- **Radix UI**: Accessible, unstyled component library

### **Development Environment**

- **Docker-based**: Consistent development environment
- **Multiple Stacks**: Traditional (Nginx), Modern (FrankenPHP), High-performance (Octane)
- **Hot Reloading**: Vite for fast frontend development
- **Database Seeding**: Realistic test data

### **Learning Features**

- **Git Branches**: Each branch demonstrates a specific pattern
- **Working Code**: All examples are functional and tested
- **Progressive Complexity**: Start simple, add patterns as needed
- **Real-world Examples**: Practical patterns you'll actually use

## Quick Reference

### Essential Commands

```bash
# Start development environment
./bin/stack up traditional -d

# Laravel commands  
./bin/dev artisan migrate --seed
./bin/dev composer install
./bin/dev npm install && npm run build

# Development workflow
./bin/dev npm run dev        # Hot reloading
./bin/dev artisan tinker     # Interactive shell
./bin/dev artisan test       # Run tests

# Switch learning branches
git checkout feature/repository-pattern
./bin/dev artisan migrate:fresh --seed
```

### Key URLs

- **Application**: http://localhost
- **FrankenPHP**: http://localhost:8080
- **Octane**: http://localhost:8000

### Learning Path

1. **Start Here**: [Getting Started](getting-started.md)
2. **Understand Why**: [Architecture Overview](architecture/overview.md)  
3. **Pick a Pattern**: [Tutorials](tutorials/) or [Branch Guide](branches/branch-guide.md)
4. **Need Help**: [Commands](reference/commands.md) or [Troubleshooting](reference/troubleshooting.md)

## Using This Documentation

### Documentation Philosophy

This documentation focuses on **learning and understanding** rather than exhaustive technical details:

- **Why over What**: Explains reasoning behind architectural decisions
- **Progressive Complexity**: Start simple, add advanced concepts gradually
- **Practical Examples**: Real-world code you can use immediately
- **Reference without Duplication**: Links to actual config files instead of copying them

### Finding What You Need

- **New to the Project**: Start with [Getting Started](getting-started.md)
- **Specific Pattern**: Check [Tutorials](tutorials/) for step-by-step guides
- **Quick Lookup**: Use [Command Reference](reference/commands.md)
- **Troubleshooting**: See [Troubleshooting Guide](reference/troubleshooting.md)
- **Understanding Decisions**: Read [Architecture Overview](architecture/overview.md)

## Contributing

Want to improve the documentation or add new tutorials?

1. **Documentation**: Focus on explaining "why" not just "how"
2. **Tutorials**: Include working code with tests
3. **Examples**: Use realistic scenarios, not contrived ones
4. **Updates**: Keep cross-references current

## Getting Help

If you get stuck:

1. Check the [Troubleshooting Guide](reference/troubleshooting.md)
2. Review the relevant tutorial or branch
3. Open an issue with:
   - What you're trying to learn
   - What step you're stuck on
   - Error messages or unexpected behavior

This project is designed to help you learn Laravel patterns through working code examples. Each piece of documentation serves that goal!
