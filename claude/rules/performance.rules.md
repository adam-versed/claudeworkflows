# Performance Optimization Rules

## Frontend Performance

### Code Splitting and Lazy Loading

```tsx
import { lazy, Suspense } from "react";
import dynamic from "next/dynamic";

// Next.js dynamic import with loading state
const HeavyChart = dynamic(() => import("@/components/HeavyChart"), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Disable SSR for client-only components
});

// React lazy loading for route-level splitting
const AdminDashboard = lazy(() => import("@/pages/AdminDashboard"));
const UserProfile = lazy(() => import("@/pages/UserProfile"));

// Route-based code splitting
export function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/admin"
          element={
            <Suspense fallback={<AdminSkeleton />}>
              <AdminDashboard />
            </Suspense>
          }
        />
        <Route
          path="/profile"
          element={
            <Suspense fallback={<ProfileSkeleton />}>
              <UserProfile />
            </Suspense>
          }
        />
      </Routes>
    </Router>
  );
}

// Component-level code splitting
const LazyModal = lazy(() =>
  import("@/components/Modal").then((module) => ({
    default: module.Modal,
  })),
);

// Conditional loading based on feature flags
const FeatureComponent = dynamic(() => import("@/components/NewFeature"), {
  loading: () => <FeatureSkeleton />,
  ssr: false,
});
```

### Image Optimization

```tsx
import Image from "next/image";
import { useState } from "react";

// Optimized image component with responsive sizing
export function OptimizedImage({ src, alt, priority = false }: ImageProps) {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <div className="relative overflow-hidden">
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
      <Image
        src={src}
        alt={alt}
        width={1200}
        height={600}
        priority={priority} // Load eagerly for above-the-fold images
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,..." // Generated blur placeholder
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        className={`transition-opacity duration-300 ${
          isLoading ? "opacity-0" : "opacity-100"
        }`}
        onLoad={() => setIsLoading(false)}
        quality={85} // Optimize quality vs size
      />
    </div>
  );
}

// Progressive image loading
export function ProgressiveImage({
  src,
  placeholder,
  alt,
}: ProgressiveImageProps) {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [imageRef, setImageRef] = useState<HTMLImageElement>();

  useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      setImageSrc(src);
    };
    setImageRef(img);
  }, [src]);

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={`transition-all duration-300 ${
        imageSrc === placeholder ? "blur-sm" : "blur-0"
      }`}
    />
  );
}

// WebP with fallback
export function WebPImage({ src, alt, ...props }: ImageProps) {
  return (
    <picture>
      <source srcSet={`${src}.webp`} type="image/webp" />
      <source srcSet={`${src}.jpg`} type="image/jpeg" />
      <img src={`${src}.jpg`} alt={alt} {...props} />
    </picture>
  );
}
```

### React Performance Optimization

```tsx
import { memo, useCallback, useMemo, useState } from "react";

// Memoization for expensive operations
const ExpensiveComponent = memo<Props>(({ data, filter, onUpdate }) => {
  // Memoize expensive calculations
  const filteredData = useMemo(() => {
    console.log("Filtering data..."); // This should only log when data or filter changes
    return data
      .filter((item) => item.status === filter)
      .sort((a, b) => b.date.getTime() - a.date.getTime())
      .slice(0, 100);
  }, [data, filter]);

  // Memoize computed values
  const statistics = useMemo(
    () => ({
      total: filteredData.length,
      completed: filteredData.filter((item) => item.completed).length,
      average:
        filteredData.reduce((sum, item) => sum + item.value, 0) /
        filteredData.length,
    }),
    [filteredData],
  );

  // Memoize event handlers
  const handleItemClick = useCallback(
    (itemId: string) => {
      onUpdate(itemId);
    },
    [onUpdate],
  );

  return (
    <div>
      <Statistics data={statistics} />
      <DataList items={filteredData} onItemClick={handleItemClick} />
    </div>
  );
});

// Optimized list rendering
const VirtualizedList = memo<ListProps>(({ items, renderItem }) => {
  const [visibleItems, setVisibleItems] = useState({ start: 0, end: 50 });

  // Only render visible items
  const renderedItems = useMemo(() => {
    return items
      .slice(visibleItems.start, visibleItems.end)
      .map((item, index) => (
        <div key={item.id} style={{ height: "60px" }}>
          {renderItem(item, visibleItems.start + index)}
        </div>
      ));
  }, [items, visibleItems, renderItem]);

  const handleScroll = useCallback((event: React.UIEvent) => {
    const scrollTop = event.currentTarget.scrollTop;
    const itemHeight = 60;
    const containerHeight = event.currentTarget.clientHeight;

    const start = Math.floor(scrollTop / itemHeight);
    const end = start + Math.ceil(containerHeight / itemHeight) + 5; // Buffer

    setVisibleItems({ start, end });
  }, []);

  return (
    <div style={{ height: "400px", overflow: "auto" }} onScroll={handleScroll}>
      <div style={{ height: items.length * 60 }}>
        <div
          style={{
            transform: `translateY(${visibleItems.start * 60}px)`,
          }}
        >
          {renderedItems}
        </div>
      </div>
    </div>
  );
});

// Debounced search
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

export function SearchComponent() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);

  const searchResults = useMemo(() => {
    if (!debouncedQuery) return [];
    return performSearch(debouncedQuery);
  }, [debouncedQuery]);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <SearchResults results={searchResults} />
    </div>
  );
}
```

## Backend Performance

### Database Query Optimization

```typescript
import { prisma } from "@/lib/prisma";
import { unstable_cache } from "next/cache";

// Efficient pagination with cursor
export async function getPaginatedUsers(
  cursor?: string,
  limit = 20,
  include?: {
    posts?: boolean;
    profile?: boolean;
  },
) {
  const users = await prisma.user.findMany({
    take: limit + 1,
    cursor: cursor ? { id: cursor } : undefined,
    orderBy: { createdAt: "desc" },
    select: {
      id: true,
      email: true,
      name: true,
      createdAt: true,
      // Conditionally include relations
      ...(include?.posts && {
        posts: {
          select: {
            id: true,
            title: true,
            createdAt: true,
          },
          take: 5, // Limit related data
        },
      }),
      ...(include?.profile && {
        profile: {
          select: {
            bio: true,
            avatar: true,
          },
        },
      }),
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

// Optimized aggregation queries
export async function getUserStatistics(userId: string) {
  const [user, postStats, orderStats] = await Promise.all([
    prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        name: true,
        createdAt: true,
      },
    }),
    prisma.post.aggregate({
      where: { authorId: userId },
      _count: { id: true },
      _avg: { views: true },
    }),
    prisma.order.aggregate({
      where: { userId },
      _count: { id: true },
      _sum: { total: true },
    }),
  ]);

  return {
    user,
    posts: {
      count: postStats._count.id,
      averageViews: postStats._avg.views,
    },
    orders: {
      count: orderStats._count.id,
      totalSpent: orderStats._sum.total,
    },
  };
}

// Batch operations
export async function updateMultipleUsers(
  userUpdates: { id: string; data: any }[],
) {
  const batchSize = 100;
  const results = [];

  for (let i = 0; i < userUpdates.length; i += batchSize) {
    const batch = userUpdates.slice(i, i + batchSize);

    const batchResults = await Promise.all(
      batch.map((update) =>
        prisma.user.update({
          where: { id: update.id },
          data: update.data,
        }),
      ),
    );

    results.push(...batchResults);
  }

  return results;
}

// Connection pooling optimization
export async function getOptimizedConnection() {
  return prisma.$extends({
    query: {
      $allModels: {
        async findMany({ args, query }) {
          // Add default limits to prevent accidentally large queries
          if (!args.take && !args.first) {
            args.take = 100;
          }
          return query(args);
        },
      },
    },
  });
}
```

### Caching Strategies

```typescript
import { unstable_cache } from "next/cache";
import { revalidateTag } from "next/cache";
import { Redis } from "@upstash/redis";

const redis = Redis.fromEnv();

// Next.js built-in caching
export const getCachedUser = unstable_cache(
  async (userId: string) => {
    console.log("Fetching user from database..."); // Should only log on cache miss
    return prisma.user.findUnique({
      where: { id: userId },
      include: { profile: true },
    });
  },
  ["user-detail"],
  {
    revalidate: 300, // Cache for 5 minutes
    tags: ["user"],
  },
);

// Redis caching layer
export class CacheService {
  private static defaultTTL = 300; // 5 minutes

  static async get<T>(key: string): Promise<T | null> {
    try {
      const cached = await redis.get(key);
      return cached ? JSON.parse(cached as string) : null;
    } catch (error) {
      console.error("Cache get error:", error);
      return null;
    }
  }

  static async set(
    key: string,
    value: any,
    ttl: number = this.defaultTTL,
  ): Promise<void> {
    try {
      await redis.setex(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.error("Cache set error:", error);
    }
  }

  static async invalidate(pattern: string): Promise<void> {
    try {
      const keys = await redis.keys(pattern);
      if (keys.length > 0) {
        await redis.del(...keys);
      }
    } catch (error) {
      console.error("Cache invalidation error:", error);
    }
  }

  // Cache-aside pattern
  static async getOrSet<T>(
    key: string,
    fetchFn: () => Promise<T>,
    ttl?: number,
  ): Promise<T> {
    // Try to get from cache first
    let data = await this.get<T>(key);

    if (data === null) {
      // Cache miss - fetch from source
      data = await fetchFn();
      await this.set(key, data, ttl);
    }

    return data;
  }
}

// API response caching
export async function getCachedUserProfile(userId: string) {
  return CacheService.getOrSet(
    `user:profile:${userId}`,
    async () => {
      return prisma.user.findUnique({
        where: { id: userId },
        include: {
          profile: true,
          posts: {
            take: 5,
            orderBy: { createdAt: "desc" },
          },
        },
      });
    },
    600, // 10 minutes
  );
}

// Cache invalidation on updates
export async function updateUserProfile(userId: string, data: any) {
  const user = await prisma.user.update({
    where: { id: userId },
    data,
  });

  // Invalidate related caches
  await Promise.all([
    CacheService.invalidate(`user:profile:${userId}`),
    CacheService.invalidate(`user:posts:${userId}*`),
    revalidateTag("user"),
  ]);

  return user;
}
```

### Response Optimization

```typescript
// Response compression and optimization
export function optimizeApiResponse(data: any): any {
  // Remove unnecessary fields
  const optimized = JSON.parse(
    JSON.stringify(data, (key, value) => {
      // Remove internal fields
      if (key.startsWith("_") || key === "password") {
        return undefined;
      }

      // Truncate long strings
      if (typeof value === "string" && value.length > 1000) {
        return value.substring(0, 1000) + "...";
      }

      return value;
    }),
  );

  return optimized;
}

// Response streaming for large datasets
export async function streamLargeDataset(query: any, response: NextResponse) {
  const stream = new ReadableStream({
    async start(controller) {
      let cursor: string | undefined;
      let hasMore = true;

      controller.enqueue(new TextEncoder().encode('{"items":['));

      let first = true;
      while (hasMore) {
        const batch = await prisma.user.findMany({
          take: 100,
          cursor: cursor ? { id: cursor } : undefined,
          where: query,
          orderBy: { createdAt: "desc" },
        });

        hasMore = batch.length === 100;
        if (batch.length > 0) {
          cursor = batch[batch.length - 1].id;
        }

        for (const item of batch) {
          if (!first) {
            controller.enqueue(new TextEncoder().encode(","));
          }
          controller.enqueue(new TextEncoder().encode(JSON.stringify(item)));
          first = false;
        }
      }

      controller.enqueue(new TextEncoder().encode("]}"));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "application/json",
      "Transfer-Encoding": "chunked",
    },
  });
}
```

## Bundle Optimization

### Webpack/Next.js Optimization

```javascript
// next.config.js
module.exports = {
  // Bundle analysis
  bundleAnalyzer: {
    enabled: process.env.ANALYZE === "true",
  },

  // Experimental features for performance
  experimental: {
    esmExternals: true,
    serverComponentsExternalPackages: ["@prisma/client"],
  },

  // Compression
  compress: true,

  // Image optimization
  images: {
    formats: ["image/webp", "image/avif"],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
  },

  // Webpack optimization
  webpack: (config, { isServer }) => {
    // Bundle splitting
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: "all",
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendors",
            chunks: "all",
          },
          common: {
            minChunks: 2,
            chunks: "all",
            enforce: true,
          },
        },
      };
    }

    // Tree shaking
    config.optimization.usedExports = true;
    config.optimization.sideEffects = false;

    return config;
  },

  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Headers for caching
  async headers() {
    return [
      {
        source: "/static/(.*)",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },
};
```

### Import Optimization

```typescript
// Use specific imports instead of barrel imports
// ❌ Bad - imports entire library
import _ from 'lodash';
import * as React from 'react';

// ✅ Good - tree-shakeable imports
import { debounce, throttle } from 'lodash';
import { useState, useEffect } from 'react';

// Dynamic imports for heavy libraries
const heavyLibrary = dynamic(() => import('heavy-library'), {
  ssr: false,
});

// Conditional imports
const DevTools = dynamic(
  () => import('@/components/DevTools'),
  {
    ssr: false,
    loading: () => null,
  }
);

export function App() {
  return (
    <div>
      {process.env.NODE_ENV === 'development' && <DevTools />}
    </div>
  );
}

// Preload critical resources
export function HomePage() {
  useEffect(() => {
    // Preload critical routes
    if (typeof window !== 'undefined') {
      import('@/pages/Dashboard');
      import('@/pages/Profile');
    }
  }, []);

  return <div>Home Page</div>;
}
```

## Performance Monitoring

### Performance Metrics

```typescript
// Web Vitals monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from "web-vitals";

export function initPerformanceMonitoring() {
  getCLS(console.log);
  getFID(console.log);
  getFCP(console.log);
  getLCP(console.log);
  getTTFB(console.log);
}

// Custom performance tracking
export class PerformanceTracker {
  private static marks: Map<string, number> = new Map();

  static mark(name: string): void {
    const timestamp = performance.now();
    this.marks.set(name, timestamp);
    performance.mark(name);
  }

  static measure(name: string, startMark: string, endMark?: string): number {
    if (endMark) {
      performance.measure(name, startMark, endMark);
    } else {
      performance.measure(name, startMark);
    }

    const startTime = this.marks.get(startMark);
    const endTime = endMark ? this.marks.get(endMark) : performance.now();

    if (startTime && endTime) {
      const duration = endTime - startTime;
      console.log(`${name}: ${duration.toFixed(2)}ms`);
      return duration;
    }

    return 0;
  }

  static async trackAsyncOperation<T>(
    name: string,
    operation: () => Promise<T>,
  ): Promise<T> {
    this.mark(`${name}-start`);

    try {
      const result = await operation();
      this.mark(`${name}-end`);
      this.measure(name, `${name}-start`, `${name}-end`);
      return result;
    } catch (error) {
      this.mark(`${name}-error`);
      this.measure(`${name}-error`, `${name}-start`, `${name}-error`);
      throw error;
    }
  }
}

// Usage example
export async function fetchUserData(userId: string) {
  return PerformanceTracker.trackAsyncOperation("fetch-user-data", async () => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  });
}
```

## Development Standards

### Performance Quality Checklist

- [ ] Code splitting implemented for large components
- [ ] Images optimized with proper formats and sizing
- [ ] Memoization applied to expensive computations
- [ ] Database queries optimized with proper indexing
- [ ] Caching strategies implemented at multiple levels
- [ ] Bundle size analyzed and optimized
- [ ] Performance metrics monitored
- [ ] Lazy loading for non-critical resources
- [ ] Virtualization for large lists
- [ ] Response times meet targets (< 200ms for APIs)
- [ ] First Contentful Paint < 1.5s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Cumulative Layout Shift < 0.1
