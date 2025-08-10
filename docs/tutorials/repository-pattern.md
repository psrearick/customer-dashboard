# Repository Pattern in Laravel

**Branch**: `feature/repository-pattern` (coming soon)  
**Difficulty**: Intermediate  
**Time**: 30-45 minutes

## What You'll Learn

- What the Repository Pattern is and why it exists
- How to implement repositories in Laravel
- When to use repositories vs. Eloquent models
- How to test with repositories
- Common mistakes to avoid

## Prerequisites

Before starting this tutorial, you should understand:

- Laravel Eloquent basics
- Dependency injection
- PHP interfaces
- Basic testing concepts

## The Problem

Imagine you're building an application where:

- You might switch databases (MySQL to MongoDB)
- You have complex queries scattered across controllers
- You want to mock database calls in tests
- You need to centralize data access logic

Without repositories, you might have:

```php
// In multiple controllers...
$users = User::where('status', 'active')
    ->where('created_at', '>=', now()->subDays(30))
    ->with(['posts', 'comments'])
    ->orderBy('created_at', 'desc')
    ->paginate(15);
```

This query logic is:

- Duplicated across controllers
- Hard to test without a database
- Difficult to modify consistently
- Tightly coupled to Eloquent

## The Solution

The Repository Pattern provides a layer between your application and data source.

### Step 1: Create the Repository Interface

First, define what operations your repository should support:

```php
// app/Repositories/Contracts/UserRepositoryInterface.php
namespace App\Repositories\Contracts;

interface UserRepositoryInterface
{
    public function all();
    public function find($id);
    public function create(array $data);
    public function update($id, array $data);
    public function delete($id);
    public function getActiveUsers();
    public function getRecentUsers($days = 30);
}
```

### Step 2: Implement the Repository

Create the concrete implementation:

```php
// app/Repositories/UserRepository.php
namespace App\Repositories;

use App\Models\User;
use App\Repositories\Contracts\UserRepositoryInterface;

class UserRepository implements UserRepositoryInterface
{
    protected $model;

    public function __construct(User $model)
    {
        $this->model = $model;
    }

    public function all()
    {
        return $this->model->all();
    }

    public function find($id)
    {
        return $this->model->findOrFail($id);
    }

    public function create(array $data)
    {
        return $this->model->create($data);
    }

    public function update($id, array $data)
    {
        $user = $this->find($id);
        $user->update($data);
        return $user;
    }

    public function delete($id)
    {
        return $this->find($id)->delete();
    }

    public function getActiveUsers()
    {
        return $this->model
            ->where('status', 'active')
            ->with(['posts', 'comments'])
            ->orderBy('created_at', 'desc')
            ->get();
    }

    public function getRecentUsers($days = 30)
    {
        return $this->model
            ->where('created_at', '>=', now()->subDays($days))
            ->orderBy('created_at', 'desc')
            ->paginate(15);
    }
}
```

### Step 3: Register in Service Provider

Bind the interface to the implementation:

```php
// app/Providers/RepositoryServiceProvider.php
namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use App\Repositories\Contracts\UserRepositoryInterface;
use App\Repositories\UserRepository;

class RepositoryServiceProvider extends ServiceProvider
{
    public function register()
    {
        $this->app->bind(
            UserRepositoryInterface::class,
            UserRepository::class
        );
    }
}
```

Don't forget to register the provider in `config/app.php`!

### Step 4: Use in Controllers

Now your controllers are clean and testable:

```php
// app/Http/Controllers/UserController.php
namespace App\Http\Controllers;

use App\Repositories\Contracts\UserRepositoryInterface;

class UserController extends Controller
{
    protected $userRepository;

    public function __construct(UserRepositoryInterface $userRepository)
    {
        $this->userRepository = $userRepository;
    }

    public function index()
    {
        $users = $this->userRepository->getRecentUsers();
        
        return view('users.index', compact('users'));
    }

    public function show($id)
    {
        $user = $this->userRepository->find($id);
        
        return view('users.show', compact('user'));
    }

    public function store(Request $request)
    {
        $user = $this->userRepository->create($request->validated());
        
        return redirect()->route('users.show', $user);
    }
}
```

## Testing

With repositories, testing becomes much easier:

```php
// tests/Unit/UserControllerTest.php
namespace Tests\Unit;

use Tests\TestCase;
use Mockery;
use App\Http\Controllers\UserController;
use App\Repositories\Contracts\UserRepositoryInterface;

class UserControllerTest extends TestCase
{
    public function test_index_returns_recent_users()
    {
        // Create a mock repository
        $mockRepo = Mockery::mock(UserRepositoryInterface::class);
        
        // Define expectations
        $mockRepo->shouldReceive('getRecentUsers')
            ->once()
            ->andReturn(collect(['user1', 'user2']));
        
        // Bind mock to container
        $this->app->instance(UserRepositoryInterface::class, $mockRepo);
        
        // Test the controller
        $controller = new UserController($mockRepo);
        $response = $controller->index();
        
        // Assert
        $this->assertNotNull($response);
    }
}
```

No database needed for unit tests!

## Common Pitfalls

### 1. Making Repositories Too Generic

❌ Don't create a generic repository for all models

✅ Create specific repositories for each model's needs

### 2. Exposing Eloquent Through Repositories

❌ Don't return Eloquent models from repositories

✅ Consider returning plain arrays or DTOs for true abstraction

### 3. Over-Using Repositories

❌ Don't use repositories for simple CRUD

✅ Use them when you have complex queries or need abstraction

### 4. Forgetting the Interface

❌ Don't inject concrete classes

✅ Always inject interfaces for flexibility

## When to Use This Pattern

### Use Repositories When:

- You have complex queries used in multiple places
- You might change data sources
- You want to mock database calls in tests
- You're building a large application with a team
- You need to implement caching at the data layer

### Don't Use Repositories When:

- You're building a simple CRUD application
- You're prototyping or building an MVP
- Your queries are simple and rarely reused
- You're the only developer and prefer simplicity

## Real-World Example

Here's how a production repository might look with caching:

```php
class CachedUserRepository implements UserRepositoryInterface
{
    protected $repository;
    protected $cache;

    public function __construct(UserRepository $repository, Cache $cache)
    {
        $this->repository = $repository;
        $this->cache = $cache;
    }

    public function find($id)
    {
        return $this->cache->remember("user.{$id}", 3600, function() use ($id) {
            return $this->repository->find($id);
        });
    }

    public function getActiveUsers()
    {
        return $this->cache->remember('users.active', 300, function() {
            return $this->repository->getActiveUsers();
        });
    }
}
```

## Exercise

Try implementing a `PostRepository` with these methods:

- `getPublishedPosts()`
- `getPostsByAuthor($userId)`
- `getPopularPosts($limit = 10)`
- `searchPosts($query)`

## Summary

The Repository Pattern:

- Abstracts data access logic
- Makes testing easier
- Centralizes query logic
- Provides flexibility for future changes

But remember: it adds complexity. Use it when the benefits outweigh the costs.

## Further Reading

- [Martin Fowler on Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Laravel Documentation on Service Container](https://laravel.com/docs/container)
- [Testing in Laravel](https://laravel.com/docs/testing)

## Next Steps

After mastering repositories, learn about:

- [Service Layer](service-layer.md) - Business logic organization
- [Action Classes](action-classes.md) - Single-purpose operations
- [Data Transfer Objects](dto.md) - Type-safe data passing