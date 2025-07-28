# React & TypeScript Development Rules

## Component Structure Standards

### TypeScript Interface Patterns
```tsx
// Well-structured React component with TypeScript
import { useState, useCallback, useMemo, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import type { User } from '@/types/user';

interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
  className?: string;
}

export function UserProfile({ userId, onUpdate, className }: UserProfileProps) {
  const { toast } = useToast();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Implementation follows...
}
```

### React Hooks Best Practices
```tsx
// Fetch user data with proper error handling
const fetchUser = useCallback(async () => {
  try {
    setIsLoading(true);
    setError(null);
    
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    
    const data = await response.json();
    setUser(data);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'An error occurred');
    toast({
      title: "Error",
      description: "Failed to load user profile",
      variant: "destructive",
    });
  } finally {
    setIsLoading(false);
  }
}, [userId, toast]);

// Update user with optimistic updates
const handleUpdate = useCallback(async (formData: FormData) => {
  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: 'PATCH',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to update user');
    }
    
    const updatedUser = await response.json();
    setUser(updatedUser);
    onUpdate?.(updatedUser);
    setIsEditing(false);
    
    toast({
      title: "Success",
      description: "Profile updated successfully",
    });
  } catch (err) {
    toast({
      title: "Error",
      description: "Failed to update profile",
      variant: "destructive",
    });
  }
}, [userId, onUpdate, toast]);

// Memoized computed values
const formattedDate = useMemo(() => {
  if (!user?.createdAt) return '';
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(user.createdAt));
}, [user?.createdAt]);
```

### Component State Management
```tsx
// Loading states with skeleton
if (isLoading) {
  return <UserProfileSkeleton className={className} />;
}

// Error states with retry capability
if (error) {
  return (
    <Card className={cn("w-full", className)}>
      <CardContent className="py-8">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchUser}
            className="mt-4"
          >
            Try Again
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Empty states
if (!user) {
  return (
    <Card className={cn("w-full", className)}>
      <CardContent className="py-8">
        <p className="text-center text-sm text-muted-foreground">
          User not found
        </p>
      </CardContent>
    </Card>
  );
}
```

### Loading Skeletons
```tsx
// Loading skeleton component
function UserProfileSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <Skeleton className="h-8 w-48" />
      </CardHeader>
      <CardContent className="space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </CardContent>
    </Card>
  );
}
```

## State Management with Zustand

### Store Structure
```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
}

interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        user: null,
        isAuthenticated: false,
        isLoading: true,
        
        // Actions with proper error handling
        login: async (email, password) => {
          try {
            set((state) => {
              state.isLoading = true;
            });
            
            const response = await fetch('/api/auth/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password }),
            });
            
            if (!response.ok) {
              throw new Error('Login failed');
            }
            
            const { user } = await response.json();
            
            set((state) => {
              state.user = user;
              state.isAuthenticated = true;
              state.isLoading = false;
            });
          } catch (error) {
            set((state) => {
              state.isLoading = false;
            });
            throw error;
          }
        },
        
        // Other actions...
      })),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    )
  )
);
```

## Component Testing Standards

### Testing Library Setup
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { UserProfile } from '@/components/UserProfile';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Test utilities
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('UserProfile', () => {
  const mockUser = {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com',
    createdAt: '2024-01-01T00:00:00Z',
  };
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('should render user information', async () => {
    // Mock API call
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockUser,
    });
    
    render(<UserProfile userId="123" />, { wrapper: createWrapper() });
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
  
  it('should handle edit mode', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockUser,
    });
    
    render(
      <UserProfile userId="123" onUpdate={onUpdate} />,
      { wrapper: createWrapper() }
    );
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    // Click edit button
    await user.click(screen.getByText('Edit'));
    
    // Should show form
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
  });
  
  it('should handle errors gracefully', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));
    
    render(<UserProfile userId="123" />, { wrapper: createWrapper() });
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch user')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });
});
```

## Performance Optimization

### Code Splitting and Lazy Loading
```tsx
import { lazy, Suspense } from 'react';
import dynamic from 'next.js';

// Next.js dynamic import with loading state
const HeavyChart = dynamic(
  () => import('@/components/HeavyChart'),
  {
    loading: () => <ChartSkeleton />,
    ssr: false, // Disable SSR for client-only components
  }
);

// React lazy loading
const AdminDashboard = lazy(() => import('@/components/AdminDashboard'));

// Memoization for expensive operations
const ExpensiveComponent = memo<Props>(({ data, filter }) => {
  const filteredData = useMemo(() => {
    return data
      .filter(item => item.status === filter)
      .sort((a, b) => b.date - a.date)
      .slice(0, 100);
  }, [data, filter]);
  
  return <DataList items={filteredData} />;
});
```

## Development Standards

### Component Quality Checklist
- [ ] TypeScript types are comprehensive and accurate
- [ ] Component handles loading, error, and empty states
- [ ] Proper React hooks usage with dependencies
- [ ] Accessibility attributes and ARIA labels
- [ ] Responsive design with proper breakpoints
- [ ] Error boundaries for fallback UI
- [ ] Performance optimized with memoization
- [ ] Comprehensive test coverage
- [ ] Clean, readable, and maintainable code
- [ ] Proper prop validation and defaults