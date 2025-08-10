# Frontend Development Guide

This guide covers frontend development with React 19, Inertia.js, and Radix UI in the Customer Dashboard application.

## Technology Stack

- **React 19.1.0** - Latest React with compiler and new features
- **Inertia.js 2** - SPA experience without API complexity
- **TypeScript** - Full type safety across the application
- **Radix UI** - Accessible, unstyled component library
- **Tailwind CSS 4** - Utility-first styling
- **Vite** - Fast build tool with hot module replacement

## Development Workflow

### Starting Development

```bash
# Start your preferred Docker stack
./stack.sh up traditional -d

# Install frontend dependencies (first time)
npm install

# Start Vite development server with hot reloading
npm run dev

# Or with host binding for Docker access
npm run dev:host
```

### Available Commands

```bash
# Development
npm run dev              # Start Vite dev server
npm run dev:host         # Start with host binding for Docker

# Production
npm run build            # Build optimized assets
npm run preview          # Preview production build

# Code Quality
npm run type-check       # TypeScript type checking
npm run lint             # Linting (placeholder - add ESLint later)
```

## Project Structure

```
resources/js/
├── Components/          # Reusable React components
│   ├── Button.tsx      # Accessible button with variants
│   ├── Card.tsx        # Card component family
│   └── ...             # Other shared components
├── Layouts/            # Application layouts
│   └── AppLayout.tsx   # Main application layout with header
├── lib/                # Utility functions and configurations
│   └── utils.ts        # className merging utilities
├── Pages/              # Inertia page components
│   ├── Welcome.tsx     # Landing page with demos
│   ├── Dashboard.tsx   # Sample dashboard
│   └── ...             # Other pages
├── types/              # TypeScript type definitions
│   └── index.d.ts      # Global types and interfaces
└── app.tsx             # Main application entry point
```

## React 19 Features

### New Hooks Available

```tsx
import { useOptimistic, useFormStatus, use } from 'react';

// Optimistic updates for better UX
const [optimisticState, addOptimistic] = useOptimistic(
    state,
    (currentState, optimisticValue) => {
        // Return new state with optimistic update
        return { ...currentState, ...optimisticValue };
    }
);

// Form status for better form handling
function SubmitButton() {
    const { pending } = useFormStatus();
    
    return (
        <button type="submit" disabled={pending}>
            {pending ? 'Submitting...' : 'Submit'}
        </button>
    );
}

// Use API for reading resources
function Profile({ userPromise }) {
    const user = use(userPromise); // Suspends until resolved
    return <div>Hello {user.name}</div>;
}
```

### React Compiler Benefits

React 19 includes a built-in compiler that automatically optimizes your components:

- **Automatic Memoization**: No need for manual `useMemo`, `useCallback`
- **Optimized Re-renders**: Compiler eliminates unnecessary re-renders
- **Better Performance**: Cleaner code with automatic optimizations

## Inertia.js Integration

### Creating New Pages

1. **Create the React Component** in `resources/js/Pages/`:

```tsx
// resources/js/Pages/NewPage.tsx
import React from 'react';
import { PageProps } from '@/types';
import AppLayout from '@/Layouts/AppLayout';

interface NewPageProps extends PageProps {
    // Add specific props for this page
    data: {
        title: string;
        items: Array<{ id: number; name: string }>;
    };
}

export default function NewPage({ data }: NewPageProps) {
    return (
        <AppLayout title="New Page">
            <div className="space-y-6">
                <h1 className="text-2xl font-bold">{data.title}</h1>
                
                <div className="grid gap-4">
                    {data.items.map(item => (
                        <div key={item.id} className="p-4 bg-white rounded-lg shadow">
                            {item.name}
                        </div>
                    ))}
                </div>
            </div>
        </AppLayout>
    );
}
```

2. **Create the Laravel Route**:

```php
// routes/web.php
Route::get('/new-page', function () {
    return Inertia::render('NewPage', [
        'data' => [
            'title' => 'My New Page',
            'items' => collect(range(1, 5))->map(fn($i) => [
                'id' => $i,
                'name' => "Item {$i}"
            ])
        ]
    ]);
})->name('new-page');
```

### Navigation Between Pages

```tsx
// Using Inertia Link for SPA navigation
import { Link } from '@inertiajs/react';

<Link 
    href="/dashboard" 
    className="text-blue-600 hover:text-blue-800"
>
    Go to Dashboard
</Link>

// Programmatic navigation
import { router } from '@inertiajs/react';

const handleClick = () => {
    router.visit('/dashboard', {
        method: 'get',
        preserveState: true,
        preserveScroll: true
    });
};
```

### Form Handling with Inertia

```tsx
import { useForm } from '@inertiajs/react';

function ContactForm() {
    const { data, setData, post, processing, errors } = useForm({
        name: '',
        email: '',
        message: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        post('/contact', {
            onSuccess: () => {
                // Handle success
            }
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <input
                type="text"
                value={data.name}
                onChange={(e) => setData('name', e.target.value)}
                className="w-full p-2 border rounded"
            />
            {errors.name && <p className="text-red-600">{errors.name}</p>}
            
            <button 
                type="submit" 
                disabled={processing}
                className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            >
                {processing ? 'Sending...' : 'Send Message'}
            </button>
        </form>
    );
}
```

## Radix UI Components

### Using Existing Components

```tsx
import { Button } from '@/Components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/Components/Card';

function MyComponent() {
    return (
        <Card>
            <CardHeader>
                <CardTitle>My Card</CardTitle>
            </CardHeader>
            <CardContent>
                <p>Card content goes here.</p>
                <Button variant="default" size="lg">
                    Primary Action
                </Button>
                <Button variant="secondary" size="sm">
                    Secondary Action
                </Button>
            </CardContent>
        </Card>
    );
}
```

### Creating New Radix Components

```tsx
// resources/js/Components/Tooltip.tsx
import React from 'react';
import * as RadixTooltip from '@radix-ui/react-tooltip';
import { cn } from '@/lib/utils';

interface TooltipProps {
    content: string;
    children: React.ReactNode;
    side?: 'top' | 'right' | 'bottom' | 'left';
}

export function Tooltip({ content, children, side = 'top' }: TooltipProps) {
    return (
        <RadixTooltip.Provider>
            <RadixTooltip.Root>
                <RadixTooltip.Trigger asChild>
                    {children}
                </RadixTooltip.Trigger>
                <RadixTooltip.Portal>
                    <RadixTooltip.Content
                        side={side}
                        className={cn(
                            'px-2 py-1 text-sm bg-gray-900 text-white rounded',
                            'shadow-lg animate-in fade-in-0 zoom-in-95'
                        )}
                    >
                        {content}
                        <RadixTooltip.Arrow className="fill-gray-900" />
                    </RadixTooltip.Content>
                </RadixTooltip.Portal>
            </RadixTooltip.Root>
        </RadixTooltip.Provider>
    );
}
```

## Styling with Tailwind CSS

### Utility Classes

The application uses Tailwind CSS 4 for styling:

```tsx
function StyledComponent() {
    return (
        <div className="max-w-4xl mx-auto p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Styled Heading
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
                    Card content
                </div>
            </div>
        </div>
    );
}
```

### Custom CSS Variables

Add custom CSS variables in `resources/css/app.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
  }
}
```

## TypeScript Usage

### Type Definitions

```tsx
// resources/js/types/index.d.ts
export interface User {
    id: number;
    name: string;
    email: string;
    email_verified_at?: string;
    avatar?: string;
}

export interface PaginatedData<T> {
    data: T[];
    current_page: number;
    last_page: number;
    per_page: number;
    total: number;
}

export type PageProps<T extends Record<string, unknown> = Record<string, unknown>> = T & {
    auth: {
        user: User;
    };
    errors: Record<string, string>;
    flash: {
        message?: string;
        error?: string;
    };
};
```

### Component Props

```tsx
interface DashboardCardProps {
    title: string;
    value: string | number;
    change?: {
        value: number;
        type: 'increase' | 'decrease';
        period: string;
    };
    icon?: React.ReactNode;
    onClick?: () => void;
}

export function DashboardCard({ 
    title, 
    value, 
    change, 
    icon, 
    onClick 
}: DashboardCardProps) {
    return (
        <Card className={cn('cursor-pointer', onClick && 'hover:shadow-md')} onClick={onClick}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                {icon}
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                {change && (
                    <p className="text-xs text-muted-foreground">
                        {change.type === 'increase' ? '+' : '-'}{change.value}% from {change.period}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}
```

## Performance Best Practices

### Code Splitting

```tsx
// Lazy load pages for better performance
import { lazy } from 'react';

const Dashboard = lazy(() => import('./Pages/Dashboard'));
const Settings = lazy(() => import('./Pages/Settings'));

// Use with Suspense
<Suspense fallback={<div>Loading...</div>}>
    <Dashboard />
</Suspense>
```

### Asset Optimization

```typescript
// vite.config.js optimizations are already included
// Assets are automatically optimized during build
```

### React 19 Optimizations

```tsx
// Let React Compiler handle optimization automatically
// No need for manual memoization in most cases

// Before React 19 (avoid this pattern now)
const MemoizedComponent = memo(({ data }) => {
    return <ExpensiveComponent data={data} />;
});

// React 19 (preferred - let compiler optimize)
function OptimizedComponent({ data }) {
    return <ExpensiveComponent data={data} />;
}
```

## Testing (Future Enhancement)

When adding tests, consider these tools:
- **Vitest** - Fast testing framework
- **React Testing Library** - Component testing
- **Inertia Test Helpers** - Testing Inertia interactions

## Debugging

### React DevTools

Install React DevTools browser extension for debugging:
- Component tree inspection
- Props and state viewing
- Performance profiling

### Vite DevTools

During development:
- Hot Module Replacement (HMR)
- Fast refresh for React components
- Source maps for debugging

### Inertia DevTools

Check browser Network tab:
- Inertia requests (XHR with special headers)
- Partial reloads
- Form submissions

## Common Patterns

### Error Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
    return (
        <div className="p-6 bg-red-50 rounded-lg">
            <h2 className="text-lg font-semibold text-red-800">Something went wrong</h2>
            <pre className="mt-2 text-sm text-red-600">{error.message}</pre>
            <button 
                onClick={resetErrorBoundary}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded"
            >
                Try again
            </button>
        </div>
    );
}

// Wrap components with error boundaries
<ErrorBoundary FallbackComponent={ErrorFallback}>
    <MyComponent />
</ErrorBoundary>
```

### Loading States

```tsx
import { useState, useTransition } from 'react';

function MyComponent() {
    const [isPending, startTransition] = useTransition();
    
    const handleAction = () => {
        startTransition(() => {
            // Perform action that might take time
            updateSomething();
        });
    };
    
    return (
        <button 
            onClick={handleAction} 
            disabled={isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
            {isPending ? 'Loading...' : 'Submit'}
        </button>
    );
}
```

This guide provides a comprehensive overview of frontend development in the Customer Dashboard application. The combination of React 19, Inertia.js, and Radix UI provides a powerful, modern, and accessible foundation for building complex user interfaces.