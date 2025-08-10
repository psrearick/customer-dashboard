# Branch Guide

This guide explains what each git branch in this repository demonstrates. Each branch represents a step in the evolution
of a Laravel application, showing different patterns and techniques.

## Branch Strategy

This repository uses branches as **living examples** rather than just version control. Each branch demonstrates a
specific Laravel technique or pattern that you can:

- Check out and explore
- Compare with other approaches
- Use as a reference in your own projects
- Follow along with blog tutorials

## Main Branch

### `main`

**Focus**: Modern Laravel Foundation  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Laravel 12 with all latest features
- React 19 + Inertia.js SPA experience
- Docker development environment
- Modern frontend tooling (Vite, TypeScript)
- Basic CRUD operations
- Database migrations and seeders

**Key files to explore**:

- `resources/js/` - React 19 components
- `app/Http/Controllers/` - Basic controllers
- `database/migrations/` - Database structure
- `routes/web.php` - Inertia routes

**When to use this branch**:

- Starting a new Laravel project
- Learning modern Laravel + React patterns
- Understanding Inertia.js basics

## Pattern Implementation Branches

### `feature/repository-pattern`

**Focus**: Data Layer Abstraction  
**Tutorial**: [Repository Pattern](../tutorials/repository-pattern.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Repository interfaces for data access
- Service provider bindings
- Dependency injection patterns
- Unit testing with mocks
- Separation of business logic from data access

**Key additions**:

- `app/Repositories/` - Repository interfaces and implementations
- `app/Providers/RepositoryServiceProvider.php` - Service bindings
- `tests/Unit/` - Unit tests with mocked repositories

**When to study this**:

- Building applications that might switch databases
- Need to centralize complex queries
- Want to improve testability
- Working on enterprise applications

### `feature/service-layer`

**Focus**: Business Logic Organization  
**Tutorial**: [Service Layer](../tutorials/service-layer.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Service classes for business logic
- Transaction handling
- Multi-step operations
- Error handling patterns
- Integration between models

**Key additions**:

- `app/Services/` - Business logic services
- `app/Exceptions/` - Custom business exceptions
- Complex workflows spanning multiple models

**When to study this**:

- Business logic is getting complex
- Operations span multiple models
- Need better error handling
- Want reusable business operations

### `feature/action-classes`

**Focus**: Single-Responsibility Operations  
**Tutorial**: [Action Classes](../tutorials/action-classes.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Single-purpose action classes
- Command pattern implementation
- Queued actions
- Action validation and authorization
- Composite actions

**Key additions**:

- `app/Actions/` - Single-purpose action classes
- Integration with Laravel's queue system
- Action-based authorization

**When to study this**:

- Breaking down complex operations
- Need queueable business logic
- Want better testability
- Building event-driven architecture

## API Development Branches

### `feature/api-resources`

**Focus**: API Development with Resources  
**Tutorial**: [API Resources](../tutorials/api-resources.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- API resource transformers
- Pagination with APIs
- API versioning
- Error handling for APIs
- API authentication (Sanctum)

**Key additions**:

- `app/Http/Resources/` - API transformers
- `routes/api.php` - API routes
- API middleware and error handling

**When to study this**:

- Building REST APIs
- Need data transformation
- Building mobile app backends
- Learning API best practices

### `feature/graphql-api`

**Focus**: GraphQL API Implementation  
**Tutorial**: [GraphQL with Laravel](../tutorials/graphql.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- GraphQL schema definition
- Resolvers and mutations
- N+1 query prevention
- GraphQL authentication
- Subscriptions for real-time

**Key additions**:

- GraphQL schema files
- Resolver classes
- GraphQL-specific middleware

**When to study this**:

- Alternative to REST APIs
- Frontend teams want flexible queries
- Building real-time applications
- Exploring modern API patterns

## Testing Branches

### `feature/testing-strategies`

**Focus**: Comprehensive Testing Approaches  
**Tutorial**: [Testing Strategies](../tutorials/testing-strategies.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Unit, feature, and integration tests
- Test factories and seeders
- Mocking external services
- Database testing patterns
- Browser testing with Dusk

**Key additions**:

- Comprehensive test suite
- Test helpers and traits
- CI/CD configuration
- Coverage reporting

**When to study this**:

- Building reliable applications
- Learning TDD/BDD approaches
- Setting up CI/CD
- Enterprise development practices

### `feature/tdd-approach`

**Focus**: Test-Driven Development  
**Tutorial**: [TDD with Laravel](../tutorials/tdd.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Red-Green-Refactor cycle
- Writing tests before code
- TDD with Laravel features
- Refactoring with confidence

**Key additions**:

- Step-by-step TDD examples
- Test-first implementation patterns
- Refactoring techniques

**When to study this**:

- Learning TDD methodology
- Want better code design
- Building critical features
- Improving code quality

## Performance Branches

### `feature/caching-strategies`

**Focus**: Application Caching  
**Tutorial**: [Caching Strategies](../tutorials/caching-strategies.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Model caching patterns
- Query result caching
- Fragment caching in views
- Cache invalidation strategies
- Redis advanced features

**Key additions**:

- Cached repository implementations
- Cache tags and invalidation
- Performance monitoring

**When to study this**:

- Application performance issues
- High-traffic scenarios
- Database optimization
- Redis usage patterns

### `feature/queue-optimization`

**Focus**: Background Job Processing  
**Tutorial**: [Queue Implementation](../tutorials/queue-implementation.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Job queue setup
- Failed job handling
- Job chaining and batching
- Queue monitoring
- Supervisor configuration

**Key additions**:

- Background job classes
- Queue configuration
- Job monitoring dashboard

**When to study this**:

- Slow operations blocking requests
- Email sending optimization
- File processing workflows
- Scalability improvements

### `feature/octane-optimization`

**Focus**: Laravel Octane Performance  
**Tutorial**: [Laravel Octane](../tutorials/octane-setup.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Octane setup and configuration
- Memory leak prevention
- State management in long-running processes
- Performance benchmarking
- Octane-specific patterns

**Key additions**:

- Octane configuration files
- Memory-safe patterns
- Performance tests

**When to study this**:

- Maximum Laravel performance
- High-concurrency requirements
- Modern deployment strategies
- Performance optimization

## Frontend Branches

### `feature/advanced-inertia`

**Focus**: Advanced Inertia.js Patterns  
**Tutorial**: [Inertia.js Patterns](../tutorials/inertia-patterns.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Partial reloads and optimization
- Form handling best practices
- File uploads with progress
- Real-time updates
- State management patterns

**Key additions**:

- Advanced React components
- Custom Inertia middleware
- Frontend state management

**When to study this**:

- Building complex SPAs
- Optimizing frontend performance
- Advanced user interactions
- Real-time features

### `feature/real-time`

**Focus**: WebSockets and Broadcasting  
**Tutorial**: [Real-time Features](../tutorials/real-time.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- WebSocket setup (Pusher/Soketi)
- Event broadcasting
- Real-time notifications
- Live chat implementation
- Presence channels

**Key additions**:

- Broadcasting configuration
- Real-time React components
- WebSocket event handlers

**When to study this**:

- Building collaborative features
- Live notifications
- Chat applications
- Real-time dashboards

## Enterprise Branches

### `feature/multi-tenancy`

**Focus**: Multi-Tenant Architecture  
**Tutorial**: [Multi-Tenancy](../tutorials/multi-tenancy.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Tenant identification strategies
- Database per tenant vs shared database
- Tenant-aware models
- Subdomain routing
- Tenant isolation

**Key additions**:

- Multi-tenancy middleware
- Tenant-aware Eloquent models
- Database switching logic

**When to study this**:

- SaaS application development
- Customer data isolation
- Scalable architecture patterns
- Enterprise requirements

### `feature/authorization`

**Focus**: Advanced Authorization  
**Tutorial**: [Authorization Patterns](../tutorials/authorization.md)  
**Blog Post**: [Coming Soon]

**What it demonstrates**:

- Role-based permissions
- Resource-based authorization
- Policy inheritance
- API authorization
- Frontend authorization

**Key additions**:

- Permission system
- Advanced policies
- Role hierarchy

**When to study this**:

- Complex permission systems
- Enterprise security requirements
- Role-based access control
- API security

## How to Use This Guide

### 1. Choose Your Learning Path

**Beginner Path**:

1. `main` - Foundation
2. `feature/testing-strategies` - Quality basics
3. `feature/api-resources` - API fundamentals

**Intermediate Path**:

1. `feature/repository-pattern` - Data abstraction
2. `feature/service-layer` - Business logic
3. `feature/caching-strategies` - Performance

**Advanced Path**:

1. `feature/action-classes` - Advanced patterns
2. `feature/octane-optimization` - Performance
3. `feature/multi-tenancy` - Enterprise features

### 2. Switching Between Branches

```bash
# List all branches
git branch -a

# Switch to a specific branch
git checkout feature/repository-pattern

# Reset database for the new branch
./bin/dev artisan migrate:fresh --seed

# Install any new dependencies
./bin/dev composer install
./bin/dev npm install
./bin/dev npm run build
```

### 3. Comparing Branches

```bash
# See differences between branches
git diff main..feature/repository-pattern

# See file changes
git diff --name-only main..feature/service-layer

# Compare specific files
git diff main:app/Http/Controllers/UserController.php feature/repository-pattern:app/Http/Controllers/UserController.php
```

## Branch Creation Guidelines

When creating new branches for this project:

1. **Naming**: Use `feature/` prefix followed by the pattern name
2. **Documentation**: Each branch should have a clear README
3. **Incremental**: Build on previous patterns when logical
4. **Tested**: Include tests demonstrating the pattern
5. **Realistic**: Use practical, not contrived examples

## Upcoming Branches

Vote for which branches you'd like to see next:

- `feature/event-sourcing` - Event-driven architecture
- `feature/microservices` - Service decomposition
- `feature/ddd-patterns` - Domain-driven design
- `feature/hexagonal-architecture` - Ports and adapters
- `feature/monitoring` - Application monitoring

## Contributing

Want to contribute a branch?

1. Open an issue describing the pattern
2. Create a feature branch
3. Implement the pattern with tests
4. Document it thoroughly
5. Submit a pull request

Each branch helps developers learn Laravel patterns through working code examples!