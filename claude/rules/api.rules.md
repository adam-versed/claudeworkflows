# API Development Rules

## API Route Structure

### Next.js API Route Pattern
```typescript
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { prisma } from '@/lib/prisma';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { rateLimit } from '@/lib/rate-limit';

// Input validation schema
const updateUserSchema = z.object({
  name: z.string().min(2).max(100).optional(),
  email: z.string().email().optional(),
  bio: z.string().max(500).optional(),
});

export async function GET(
  request: NextRequest,
  { params }: { params: { userId: string } }
) {
  try {
    // Rate limiting
    const identifier = request.ip ?? 'anonymous';
    const { success } = await rateLimit.check(identifier);
    
    if (!success) {
      return NextResponse.json(
        { error: 'Too many requests' },
        { status: 429 }
      );
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
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json(user);
  } catch (error) {
    console.error('Error fetching user:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { userId: string } }
) {
  try {
    // Authentication
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }
    
    // Authorization - users can only update their own profile
    if (session.user.id !== params.userId) {
      return NextResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      );
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
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      );
    }
    
    console.error('Error updating user:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

## Input Validation

### Zod Schema Patterns
```typescript
import { z } from 'zod';

// User registration schema
export const userRegistrationSchema = z.object({
  email: z
    .string()
    .email('Invalid email format')
    .toLowerCase()
    .max(255),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain uppercase letter')
    .regex(/[a-z]/, 'Password must contain lowercase letter')
    .regex(/[0-9]/, 'Password must contain number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain special character'),
  name: z
    .string()
    .min(2, 'Name too short')
    .max(100, 'Name too long')
    .regex(/^[a-zA-Z\s'-]+$/, 'Invalid characters in name'),
});

// Product creation schema
export const productSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().min(10).max(2000),
  price: z.number().positive().max(999999.99),
  category: z.enum(['electronics', 'clothing', 'books', 'home']),
  tags: z.array(z.string().min(1).max(50)).max(10),
  inStock: z.boolean(),
  sku: z.string().regex(/^[A-Z0-9-]+$/, 'Invalid SKU format'),
});

// Query parameter validation
export const paginationSchema = z.object({
  page: z.string().regex(/^\d+$/).transform(Number).refine(n => n >= 1),
  limit: z.string().regex(/^\d+$/).transform(Number).refine(n => n >= 1 && n <= 100),
  sortBy: z.enum(['createdAt', 'updatedAt', 'name', 'price']).optional(),
  sortOrder: z.enum(['asc', 'desc']).optional(),
});
```

## Authentication & Authorization

### Session-Based Authentication
```typescript
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

// Utility function for authentication check
export async function requireAuth(request: NextRequest) {
  const session = await getServerSession(authOptions);
  
  if (!session?.user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }
  
  return session;
}

// Role-based authorization
export async function requireRole(request: NextRequest, allowedRoles: string[]) {
  const session = await requireAuth(request);
  
  if (session instanceof NextResponse) {
    return session; // Return auth error
  }
  
  if (!allowedRoles.includes(session.user.role)) {
    return NextResponse.json(
      { error: 'Insufficient permissions' },
      { status: 403 }
    );
  }
  
  return session;
}

// Usage in API routes
export async function DELETE(
  request: NextRequest,
  { params }: { params: { userId: string } }
) {
  // Check if user has admin role
  const authResult = await requireRole(request, ['admin']);
  if (authResult instanceof NextResponse) {
    return authResult;
  }
  
  // Proceed with deletion logic
  await prisma.user.delete({
    where: { id: params.userId },
  });
  
  return NextResponse.json({ success: true });
}
```

### Resource Ownership Authorization
```typescript
// Check if user owns the resource
export async function requireResourceOwnership(
  request: NextRequest,
  resourceId: string,
  resourceType: 'user' | 'post' | 'order'
) {
  const session = await requireAuth(request);
  
  if (session instanceof NextResponse) {
    return session;
  }
  
  let isOwner = false;
  
  switch (resourceType) {
    case 'user':
      isOwner = session.user.id === resourceId;
      break;
    case 'post':
      const post = await prisma.post.findUnique({
        where: { id: resourceId },
        select: { authorId: true },
      });
      isOwner = post?.authorId === session.user.id;
      break;
    case 'order':
      const order = await prisma.order.findUnique({
        where: { id: resourceId },
        select: { userId: true },
      });
      isOwner = order?.userId === session.user.id;
      break;
  }
  
  if (!isOwner) {
    return NextResponse.json(
      { error: 'Access denied' },
      { status: 403 }
    );
  }
  
  return session;
}
```

## Error Handling

### Standardized Error Responses
```typescript
// Error response utility
export function createErrorResponse(
  message: string,
  status: number,
  details?: any
) {
  return NextResponse.json(
    {
      error: message,
      ...(details && { details }),
      timestamp: new Date().toISOString(),
    },
    { status }
  );
}

// Error handling middleware
export function withErrorHandling(handler: Function) {
  return async (request: NextRequest, context: any) => {
    try {
      return await handler(request, context);
    } catch (error) {
      console.error('API Error:', error);
      
      if (error instanceof z.ZodError) {
        return createErrorResponse('Invalid input', 400, error.errors);
      }
      
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        switch (error.code) {
          case 'P2002':
            return createErrorResponse('Duplicate entry', 409);
          case 'P2025':
            return createErrorResponse('Record not found', 404);
          default:
            return createErrorResponse('Database error', 500);
        }
      }
      
      return createErrorResponse('Internal server error', 500);
    }
  };
}

// Usage
export const GET = withErrorHandling(async (request: NextRequest) => {
  // Your API logic here
});
```

## Database Operations

### Efficient Query Patterns
```typescript
// Pagination with cursor
export async function getPaginatedUsers(
  cursor?: string,
  limit = 20,
  search?: string
) {
  const where = search ? {
    OR: [
      { email: { contains: search, mode: 'insensitive' } },
      { name: { contains: search, mode: 'insensitive' } },
    ],
  } : {};
  
  const users = await prisma.user.findMany({
    where,
    take: limit + 1,
    cursor: cursor ? { id: cursor } : undefined,
    orderBy: { createdAt: 'desc' },
    select: {
      id: true,
      email: true,
      name: true,
      createdAt: true,
      _count: {
        select: {
          posts: true,
          orders: true,
        },
      },
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

// Transaction example
export async function createOrderWithInventory(
  userId: string,
  items: { productId: string; quantity: number }[]
) {
  return await prisma.$transaction(async (tx) => {
    // Check inventory
    for (const item of items) {
      const product = await tx.product.findUnique({
        where: { id: item.productId },
        select: { stock: true },
      });
      
      if (!product || product.stock < item.quantity) {
        throw new Error(`Insufficient stock for product ${item.productId}`);
      }
    }
    
    // Create order
    const order = await tx.order.create({
      data: {
        userId,
        items: {
          create: items.map(item => ({
            productId: item.productId,
            quantity: item.quantity,
          })),
        },
      },
    });
    
    // Update inventory
    for (const item of items) {
      await tx.product.update({
        where: { id: item.productId },
        data: {
          stock: {
            decrement: item.quantity,
          },
        },
      });
    }
    
    return order;
  });
}
```

## Rate Limiting

### Rate Limiting Implementation
```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

// Create rate limiter
const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
});

// Rate limiting middleware
export async function withRateLimit(
  request: NextRequest,
  identifier?: string
) {
  const ip = identifier || request.ip || 'anonymous';
  const { success, limit, reset, remaining } = await ratelimit.limit(ip);
  
  if (!success) {
    return NextResponse.json(
      { 
        error: 'Too many requests',
        retryAfter: reset,
      },
      { 
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString(),
        },
      }
    );
  }
  
  return null; // Allow request
}

// Usage in API route
export async function POST(request: NextRequest) {
  const rateLimitResult = await withRateLimit(request);
  if (rateLimitResult) {
    return rateLimitResult;
  }
  
  // Continue with API logic
}
```

## API Testing Patterns

### API Route Testing
```typescript
import { createMocks } from 'node-mocks-http';
import { GET, PATCH } from '@/app/api/users/[userId]/route';
import { prisma } from '@/lib/prisma';
import { getServerSession } from 'next-auth';

// Mock dependencies
vi.mock('@/lib/prisma', () => ({
  prisma: {
    user: {
      findUnique: vi.fn(),
      update: vi.fn(),
    },
  },
}));

vi.mock('next-auth', () => ({
  getServerSession: vi.fn(),
}));

describe('/api/users/[userId]', () => {
  describe('GET', () => {
    it('should return user data', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      };
      
      prisma.user.findUnique.mockResolvedValue(mockUser);
      
      const { req } = createMocks({
        method: 'GET',
      });
      
      const response = await GET(req, { params: { userId: '123' } });
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data).toEqual(mockUser);
    });
    
    it('should return 404 for non-existent user', async () => {
      prisma.user.findUnique.mockResolvedValue(null);
      
      const { req } = createMocks({
        method: 'GET',
      });
      
      const response = await GET(req, { params: { userId: '999' } });
      const data = await response.json();
      
      expect(response.status).toBe(404);
      expect(data.error).toBe('User not found');
    });
  });
  
  describe('PATCH', () => {
    it('should update user data', async () => {
      getServerSession.mockResolvedValue({
        user: { id: '123', email: 'test@example.com' },
      });
      
      const updatedUser = {
        id: '123',
        name: 'Updated Name',
        email: 'test@example.com',
      };
      
      prisma.user.update.mockResolvedValue(updatedUser);
      
      const { req } = createMocks({
        method: 'PATCH',
        body: { name: 'Updated Name' },
      });
      
      const response = await PATCH(req, { params: { userId: '123' } });
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.name).toBe('Updated Name');
    });
    
    it('should require authentication', async () => {
      getServerSession.mockResolvedValue(null);
      
      const { req } = createMocks({
        method: 'PATCH',
        body: { name: 'Updated Name' },
      });
      
      const response = await PATCH(req, { params: { userId: '123' } });
      const data = await response.json();
      
      expect(response.status).toBe(401);
      expect(data.error).toBe('Unauthorized');
    });
  });
});
```

## Development Standards

### API Quality Checklist
- [ ] All endpoints use proper HTTP methods (GET, POST, PUT/PATCH, DELETE)
- [ ] Input validation with Zod schemas
- [ ] Authentication and authorization implemented
- [ ] Rate limiting on sensitive endpoints
- [ ] Proper error handling with status codes
- [ ] Database queries optimized
- [ ] Pagination implemented for list endpoints
- [ ] API responses follow consistent format
- [ ] Comprehensive test coverage
- [ ] Documentation with OpenAPI/Swagger
- [ ] CORS configured appropriately
- [ ] Request/response logging implemented