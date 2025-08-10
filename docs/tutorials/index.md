# Tutorials

This directory contains step-by-step tutorials that correspond to different branches in the repository. Each tutorial
teaches a specific Laravel technique or pattern.

## Available Tutorials

### Foundation

- [Getting Started](../getting-started.md) - Initial setup and orientation
- [Understanding the Architecture](../architecture/overview.md) - Why things are built this way

### Laravel Patterns (Coming Soon)

- [Repository Pattern](repository-pattern.md) - Abstract your data layer
- [Service Layer](service-layer.md) - Organize business logic
- [Action Classes](action-classes.md) - Single-responsibility operations
- [Form Requests](form-requests.md) - Validation and authorization
- [API Resources](api-resources.md) - Transform data for APIs

### Testing Approaches (Coming Soon)

- [Unit Testing](unit-testing.md) - Test individual components
- [Feature Testing](feature-testing.md) - Test user workflows
- [Browser Testing](browser-testing.md) - End-to-end testing with Dusk
- [Test-Driven Development](tdd.md) - Write tests first

### Performance Optimization (Coming Soon)

- [Database Optimization](database-optimization.md) - Indexes, queries, and relationships
- [Caching Strategies](caching-strategies.md) - When and how to cache
- [Queue Implementation](queue-implementation.md) - Background job processing
- [Laravel Octane](octane-setup.md) - High-performance Laravel

### Frontend Patterns (Coming Soon)

- [Inertia.js Patterns](inertia-patterns.md) - SPA without the API
- [React Components](react-components.md) - Building reusable UI
- [State Management](state-management.md) - Managing complex frontend state
- [Real-time Features](real-time.md) - WebSockets and broadcasting

## How to Use These Tutorials

### 1. Choose Your Learning Path

**Beginner Path**:

1. Getting Started
2. Understanding the Architecture
3. Form Requests
4. Feature Testing

**Intermediate Path**:

1. Repository Pattern
2. Service Layer
3. API Resources
4. Unit Testing

**Advanced Path**:

1. Action Classes
2. Caching Strategies
3. Queue Implementation
4. Laravel Octane

### 2. Follow Along with Branches

Each tutorial corresponds to a git branch:

```bash
# See all available branches
git branch -a

# Switch to a tutorial branch
git checkout feature/repository-pattern

# Reset database for the tutorial
./bin/dev artisan migrate:fresh --seed
```

### 3. Tutorial Structure

Each tutorial follows this structure:

1. **What You'll Learn** - Clear learning objectives
2. **Prerequisites** - What you need to know first
3. **The Problem** - Why this pattern exists
4. **The Solution** - Step-by-step implementation
5. **Testing** - How to verify it works
6. **Common Pitfalls** - Mistakes to avoid
7. **When to Use This** - Real-world applications
8. **Further Reading** - Additional resources

### 4. Code Examples

All code examples are:

- **Working**: Tested and functional
- **Realistic**: Based on actual use cases
- **Progressive**: Build on previous knowledge
- **Commented**: Explain the "why" not just the "what"

## Contributing Tutorials

Want to add a tutorial? Here's how:

1. **Create a branch**: `feature/your-tutorial-topic`
2. **Implement the feature**: Working code with tests
3. **Write the tutorial**: Follow the structure above
4. **Add to this index**: Link your tutorial
5. **Submit a PR**: Include sample data and tests

## Learning Philosophy

These tutorials follow these principles:

1. **Learn by Doing**: Every tutorial has you write code
2. **Understand Why**: Not just how, but why to use patterns
3. **See the Evolution**: Start simple, add complexity
4. **Real-World Focus**: Practical examples you'll actually use

## Support

If you get stuck:

- Check the [Troubleshooting Guide](../reference/troubleshooting.md)
- Review the branch's README
- Compare your code with the branch
- Open an issue with your question

## Tutorial Requests

Want to see a specific topic covered? Open an issue with:

- The Laravel concept you want to learn
- Your current understanding level
- What you want to build with it

Happy learning!