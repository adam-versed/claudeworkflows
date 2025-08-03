# Next.js Development Rules

## API Route Implementation

### Route Handler Structure

```typescript
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { rateLimit } from "@/lib/rate-limit";

// Input validation schema
const updateUserSchema = z.object({
  name: z.string().min(2).max(100).optional(),
  email: z.string().email().optional(),
  bio: z.string().max(500).optional(),
});

export async function GET(
  request: NextRequest,
  { params }: { params: { userId: string } },
) {
  try {
    // Rate limiting
    const identifier = request.ip ?? "anonymous";
    const { success } = await rateLimit.check(identifier);

    if (!success) {
      return NextResponse.json({ error: "Too many requests" }, { status: 429 });
    }

    // Get user
    const user = await prisma.user.findUnique({
      where: { id: params.userId },
      select: {
        id: true,
        email: true,
        name: true,
        bio: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    if (!user) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    return NextResponse.json(user);
  } catch (error) {
    console.error("Error fetching user:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { userId: string } },
) {
  try {
    // Authentication
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Authorization - users can only update their own profile
    if (session.user.id !== params.userId) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // Parse and validate input
    const body = await request.json();
    const validatedData = updateUserSchema.parse(body);

    // Update user
    const updatedUser = await prisma.user.update({
      where: { id: params.userId },
      data: {
        ...validatedData,
        updatedAt: new Date(),
      },
      select: {
        id: true,
        email: true,
        name: true,
        bio: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return NextResponse.json(updatedUser);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid input", details: error.errors },
        { status: 400 },
      );
    }

    console.error("Error updating user:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
```

## Authentication & Authorization

### Server-Side Session Handling

```typescript
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';

// In page components
export default async function ProtectedPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect('/login');
  }

  return <DashboardContent user={session.user} />;
}

// In API routes
export async function POST(request: NextRequest) {
  const session = await getServerSession(authOptions);

  if (!session?.user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  // Proceed with authenticated request
}
```

### Role-Based Access Control

```typescript
// Middleware for role checking
export function requireRole(allowedRoles: string[]) {
  return async (request: NextRequest) => {
    const session = await getServerSession(authOptions);

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    if (!allowedRoles.includes(session.user.role)) {
      return NextResponse.json(
        { error: "Insufficient permissions" },
        { status: 403 },
      );
    }

    return null; // Allow request to proceed
  };
}

// Usage in API routes
export async function DELETE(
  request: NextRequest,
  { params }: { params: { userId: string } },
) {
  const roleCheck = await requireRole(["admin", "moderator"])(request);
  if (roleCheck) return roleCheck;

  // Proceed with deletion logic
}
```

## Performance Optimization

### Image Optimization

```tsx
import Image from "next/image";

export function OptimizedImage() {
  return (
    <Image
      src="/hero-image.jpg"
      alt="Hero"
      width={1200}
      height={600}
      priority // Load eagerly for above-the-fold images
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..." // Generated blur placeholder
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    />
  );
}
```

### Caching Strategies

```typescript
import { unstable_cache } from "next/cache";
import { revalidateTag } from "next/cache";

// Database query optimization with caching
export const getCachedUser = unstable_cache(
  async (userId: string) => {
    return prisma.user.findUnique({
      where: { id: userId },
      include: { profile: true },
    });
  },
  ["user-detail"],
  {
    revalidate: 60, // Cache for 60 seconds
    tags: ["user"],
  },
);

// Revalidate cache when data changes
export async function updateUser(userId: string, data: any) {
  const user = await prisma.user.update({
    where: { id: userId },
    data,
  });

  // Invalidate related caches
  revalidateTag("user");

  return user;
}
```

### Database Query Optimization

```typescript
// Efficient pagination with cursor
export async function getPaginatedUsers(cursor?: string, limit = 20) {
  const users = await prisma.user.findMany({
    take: limit + 1,
    cursor: cursor ? { id: cursor } : undefined,
    orderBy: { createdAt: "desc" },
    select: {
      id: true,
      email: true,
      name: true,
      createdAt: true,
      // Avoid selecting large fields unless needed
    },
  });

  const hasMore = users.length > limit;
  const items = hasMore ? users.slice(0, -1) : users;

  return {
    items,
    nextCursor: hasMore ? items[items.length - 1].id : null,
    hasMore,
  };
}
```

## Data Fetching Patterns

### Server Components

```tsx
// Server component with data fetching
async function UserList() {
  const users = await prisma.user.findMany({
    select: {
      id: true,
      name: true,
      email: true,
    },
    orderBy: { createdAt: "desc" },
  });

  return (
    <div>
      {users.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

### Client Components with SWR/React Query

```tsx
"use client";

import useSWR from "swr";
import { useQuery } from "@tanstack/react-query";

// Using SWR
function UserProfile({ userId }: { userId: string }) {
  const {
    data: user,
    error,
    isLoading,
  } = useSWR(`/api/users/${userId}`, fetch);

  if (error) return <div>Failed to load</div>;
  if (isLoading) return <div>Loading...</div>;

  return <div>{user.name}</div>;
}

// Using React Query
function UserProfileQuery({ userId }: { userId: string }) {
  const {
    data: user,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetch(`/api/users/${userId}`).then((res) => res.json()),
  });

  if (error) return <div>Failed to load</div>;
  if (isLoading) return <div>Loading...</div>;

  return <div>{user.name}</div>;
}
```

## Middleware Implementation

### Request Intercepting

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";

export async function middleware(request: NextRequest) {
  // Check if path requires authentication
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    const token = await getToken({ req: request });

    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  // Rate limiting for API routes
  if (request.nextUrl.pathname.startsWith("/api/")) {
    const ip = request.ip ?? "127.0.0.1";
    const identifier = `${ip}-${request.nextUrl.pathname}`;

    // Check rate limit (implementation depends on your rate limiting library)
    const isAllowed = await checkRateLimit(identifier);

    if (!isAllowed) {
      return new NextResponse("Too Many Requests", { status: 429 });
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/:path*"],
};
```

## Error Handling

### Global Error Boundary

```tsx
// app/error.tsx
"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to external service
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-xl font-semibold mb-4">Something went wrong!</h2>
      <button
        onClick={reset}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Try again
      </button>
    </div>
  );
}
```

### API Error Responses

```typescript
// Standardized error response format
export function createErrorResponse(
  message: string,
  status: number,
  details?: any,
) {
  return NextResponse.json(
    {
      error: message,
      ...(details && { details }),
      timestamp: new Date().toISOString(),
    },
    { status },
  );
}

// Usage in API routes
export async function POST(request: NextRequest) {
  try {
    // API logic
  } catch (error) {
    if (error instanceof ValidationError) {
      return createErrorResponse("Invalid input", 400, error.details);
    }

    if (error instanceof AuthenticationError) {
      return createErrorResponse("Unauthorized", 401);
    }

    console.error("Unexpected error:", error);
    return createErrorResponse("Internal server error", 500);
  }
}
```

## Development Standards

### Next.js Quality Checklist

- [ ] API routes use proper TypeScript types
- [ ] Input validation with Zod schemas
- [ ] Authentication and authorization implemented
- [ ] Rate limiting on sensitive endpoints
- [ ] Error handling with proper status codes
- [ ] Database queries optimized with proper selects
- [ ] Caching strategies implemented where appropriate
- [ ] Image optimization with Next.js Image component
- [ ] Middleware configured for cross-cutting concerns
- [ ] Performance monitoring and logging setup
