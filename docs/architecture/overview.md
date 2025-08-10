# Architecture Overview

This document explains the architectural decisions in the Customer Dashboard project and **why** they were made.
Understanding these decisions helps you apply similar patterns in your own projects.

## Project Philosophy

This project prioritizes:

1. **Learning clarity** over premature optimization
2. **Real-world patterns** over academic theory
3. **Maintainability** over cleverness
4. **Progressive enhancement** - start simple, add complexity when needed

## Application Architecture

### Why Laravel + Inertia.js + React?

**Decision**: Use Inertia.js to bridge Laravel and React instead of building a separate API.

**Why**:

- **Simplified architecture**: No need for API authentication, CORS, or separate deployments
- **Faster development**: Use Laravel's session auth and validation directly
- **Better SEO**: Server-side routing with client-side interactivity
- **Learning focus**: Concentrate on Laravel patterns, not API design

**When to use this**:

- Building applications where the frontend and backend are tightly coupled
- Teams comfortable with both Laravel and React
- Projects that don't need a public API (yet)

**When NOT to use this**:

- Building a public API for multiple consumers
- Mobile app backends
- Microservices architecture

### Database Design Philosophy

**Decision**: Start with a simple, normalized database design.

**Why**:

- **Learning progression**: Easy to understand, then optimize
- **Laravel conventions**: Follows Eloquent's expectations
- **Flexibility**: Easy to refactor as requirements change

**Key Principles**:

```
1. Every table has an `id` primary key (Laravel convention)
2. Foreign keys follow the `{model}_id` pattern
3. Timestamps on every table for audit trails
4. Soft deletes where data retention matters
```

## Development Environment

### Why Docker?

**Decision**: Use Docker for the development environment instead of local installations.

**Why**:

- **Consistency**: Same environment for all developers and CI/CD
- **Isolation**: No conflicts with other projects
- **Learning tool**: Switch between different configurations easily
- **Real-world**: Mirrors production deployment strategies

**The Three Stack Approach**:

1. **Traditional** (Nginx + PHP-FPM): What most production servers use
2. **Modern** (FrankenPHP): Latest technology for experimentation
3. **High-Performance** (Octane): When you need maximum speed

This allows you to:

- Learn different deployment strategies
- Test performance characteristics
- Choose the right tool for each project

## Code Organization

### Directory Structure Decisions

```
app/
├── Http/
│   ├── Controllers/     # Thin controllers - routing logic only
│   ├── Requests/        # Form validation separated from controllers
│   └── Resources/       # API transformation (when needed)
├── Models/              # Eloquent models with minimal logic
├── Services/            # Business logic layer (featured in branches)
├── Repositories/        # Data access layer (featured in branches)
└── Policies/           # Authorization logic
```

**Why this structure**:

- **Separation of concerns**: Each layer has a single responsibility
- **Testability**: Business logic isolated from framework
- **Scalability**: Easy to add new features without touching existing code
- **Learning path**: Start simple (MVC), add layers as needed

### Frontend Architecture

```
resources/js/
├── Components/          # Reusable UI components
├── Layouts/            # Page templates
├── Pages/              # Inertia page components
├── lib/                # Utilities and helpers
└── types/              # TypeScript definitions
```

**Why**:

- **Component reusability**: Build once, use everywhere
- **Type safety**: Catch errors during development
- **Clear boundaries**: Easy to find and modify code

## Design Patterns Used

### Repository Pattern (feature branch)

**When to use**:

- Complex queries that don't fit in models
- Need to switch data sources (MySQL to MongoDB)
- Testing without database connections

**When it's overkill**:

- Simple CRUD operations
- Small applications
- Prototypes

### Service Layer (feature branch)

**When to use**:

- Business logic that spans multiple models
- External API integrations
- Complex calculations or workflows

**Benefits**:

- Controllers stay thin
- Business logic is reusable
- Easy to test in isolation

### Action Classes (feature branch)

**When to use**:

- Single, complex operations
- Operations that might be queued
- Reusable business logic

**Example**:

```php
class PublishArticleAction
{
    public function execute(Article $article): void
    {
        // Complex publishing logic
        // Notifications, cache clearing, etc.
    }
}
```

## Performance Considerations

### Philosophy: "Make it work, make it right, make it fast"

1. **Start simple**: Get the feature working
2. **Refactor**: Clean up the code
3. **Optimize**: Only when you have metrics showing issues

### Caching Strategy

**Levels of caching** (from simple to complex):

1. **Browser caching**: Static assets
2. **CDN**: Images and files
3. **Application cache**: Database queries (Redis)
4. **HTTP cache**: Full page caching
5. **Database cache**: Query result caching

Each branch demonstrates when and how to implement these levels.

## Security Architecture

### Defense in Depth

Multiple layers of security:

1. **Environment**: Docker isolation
2. **Network**: Proper firewall rules
3. **Application**: Laravel's built-in protections
4. **Database**: Prepared statements, validation
5. **Monitoring**: Logging and alerting

### Authentication & Authorization

**Decision**: Use Laravel's built-in auth with policies.

**Why**:

- Battle-tested and secure
- Follows industry standards
- Easy to extend
- Well-documented

## Testing Philosophy

### Testing Pyramid

```
        /\
       /  \  E2E Tests (Few)
      /    \ 
     /      \  Feature Tests (Some)
    /        \
   /          \  Unit Tests (Many)
  /____________\
```

**Why this approach**:

- **Fast feedback**: Unit tests run in milliseconds
- **Confidence**: Feature tests ensure integration works
- **User perspective**: E2E tests verify critical paths

## Deployment Considerations

### Environment Progression

```
Local -> Staging -> Production
```

**Each environment's purpose**:

- **Local**: Rapid development, debugging
- **Staging**: Integration testing, client review
- **Production**: Optimized for performance and security

### Configuration Management

**Decision**: Use environment variables for configuration.

**Why**:

- **Security**: Sensitive data not in code
- **Flexibility**: Same code, different configs
- **12-Factor App**: Industry standard practice

## Evolution Strategy

This architecture is designed to evolve:

1. **Start simple**: Basic MVC for MVPs
2. **Add patterns**: Repositories, services as needed
3. **Optimize**: Caching, queuing when metrics show need
4. **Scale**: Horizontal scaling, microservices if required

Each branch in this repository demonstrates a step in this evolution.

## Common Pitfalls to Avoid

1. **Over-engineering**: Don't add patterns you don't need yet
2. **Premature optimization**: Measure first, optimize second
3. **Framework fighting**: Work with Laravel's conventions
4. **Copy-paste architecture**: Understand why before implementing

## Further Learning

Each architectural decision has a corresponding branch or tutorial:

- `feature/repository-pattern` - Data layer abstraction
- `feature/service-layer` - Business logic organization
- `feature/caching-strategies` - Performance optimization
- `feature/testing-approaches` - Testing methodologies

Remember: Architecture is about trade-offs. There's no perfect solution, only the right solution for your specific
needs.