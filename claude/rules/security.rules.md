# Security Development Rules

## Input Validation & Sanitization

### Comprehensive Input Validation
```typescript
import { z } from 'zod';
import DOMPurify from 'isomorphic-dompurify';
import bcrypt from 'bcryptjs';

// Input validation schemas
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

// Email validation with domain blocking
export const emailValidationSchema = z
  .string()
  .email()
  .refine((email) => {
    const domain = email.split('@')[1];
    const blockedDomains = [
      'tempmail.com',
      '10minutemail.com',
      'guerrillamail.com',
      'throwaway.email'
    ];
    return !blockedDomains.includes(domain);
  }, 'Temporary email addresses are not allowed');

// File upload validation
export const fileUploadSchema = z.object({
  file: z.object({
    name: z.string().regex(/\.(jpg|jpeg|png|gif|pdf|doc|docx)$/i, 'Invalid file type'),
    size: z.number().max(10 * 1024 * 1024, 'File too large (max 10MB)'),
    type: z.string().regex(/^(image\/(jpeg|png|gif)|application\/(pdf|msword))/, 'Invalid MIME type'),
  }),
});
```

### XSS Prevention
```typescript
// HTML sanitization
export function sanitizeHtml(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
    ADD_ATTR: ['target'],
  });
}

// Safe HTML rendering component
import { useMemo } from 'react';

interface SafeHTMLProps {
  content: string;
  allowedTags?: string[];
}

export function SafeHTML({ content, allowedTags }: SafeHTMLProps) {
  const sanitizedContent = useMemo(() => {
    return DOMPurify.sanitize(content, {
      ALLOWED_TAGS: allowedTags || ['b', 'i', 'em', 'strong', 'p', 'br'],
      ALLOWED_ATTR: ['href', 'target', 'rel'],
      ALLOW_DATA_ATTR: false,
    });
  }, [content, allowedTags]);
  
  return (
    <div 
      dangerouslySetInnerHTML={{ __html: sanitizedContent }}
      className="prose"
    />
  );
}

// Content Security Policy headers
export function setCSPHeaders(response: NextResponse) {
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://trusted-cdn.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https:",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://api.yourdomain.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', csp);
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  return response;
}
```

## Authentication Security

### Secure Password Handling
```typescript
import bcrypt from 'bcryptjs';
import crypto from 'crypto';

export class PasswordSecurity {
  // Hash password with salt
  static async hashPassword(password: string): Promise<string> {
    const saltRounds = 12;
    return bcrypt.hash(password, saltRounds);
  }
  
  // Verify password
  static async verifyPassword(
    password: string, 
    hashedPassword: string
  ): Promise<boolean> {
    return bcrypt.compare(password, hashedPassword);
  }
  
  // Generate secure random password
  static generateSecurePassword(length: number = 16): string {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    
    for (let i = 0; i < length; i++) {
      const randomIndex = crypto.randomInt(0, charset.length);
      password += charset[randomIndex];
    }
    
    return password;
  }
  
  // Password strength validation
  static validatePasswordStrength(password: string): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    if (!/[^A-Za-z0-9]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }
    
    // Check for common patterns
    const commonPatterns = [
      /(.)\1{2,}/, // Repeated characters
      /123456|abcdef|qwerty/i, // Sequential patterns
    ];
    
    if (commonPatterns.some(pattern => pattern.test(password))) {
      errors.push('Password contains common patterns');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}
```

### CSRF Protection
```typescript
import { randomBytes } from 'crypto';
import { cookies } from 'next/headers';

export class CSRFProtection {
  // Generate CSRF token
  static generateToken(): string {
    return randomBytes(32).toString('hex');
  }
  
  // Set CSRF token in cookie
  static setCSRFToken(response: NextResponse): string {
    const token = this.generateToken();
    
    response.cookies.set('csrf-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 60 * 60 * 24, // 24 hours
    });
    
    return token;
  }
  
  // Verify CSRF token
  static async verifyCSRFToken(request: NextRequest): Promise<boolean> {
    const cookieStore = cookies();
    const tokenFromCookie = cookieStore.get('csrf-token')?.value;
    const tokenFromHeader = request.headers.get('x-csrf-token');
    
    if (!tokenFromCookie || !tokenFromHeader) {
      return false;
    }
    
    // Use constant-time comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(tokenFromCookie),
      Buffer.from(tokenFromHeader)
    );
  }
  
  // Middleware for CSRF protection
  static createMiddleware() {
    return async (request: NextRequest) => {
      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
        const isValid = await this.verifyCSRFToken(request);
        
        if (!isValid) {
          return NextResponse.json(
            { error: 'Invalid CSRF token' },
            { status: 403 }
          );
        }
      }
      
      return NextResponse.next();
    };
  }
}
```

## Rate Limiting & Abuse Prevention

### Advanced Rate Limiting
```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

export class SecurityRateLimit {
  private static redis = Redis.fromEnv();
  
  // Different rate limits for different endpoints
  private static limiters = {
    // General API
    api: new Ratelimit({
      redis: this.redis,
      limiter: Ratelimit.slidingWindow(100, '1 m'),
    }),
    
    // Authentication endpoints
    auth: new Ratelimit({
      redis: this.redis,
      limiter: Ratelimit.slidingWindow(5, '15 m'),
    }),
    
    // Password reset
    passwordReset: new Ratelimit({
      redis: this.redis,
      limiter: Ratelimit.slidingWindow(3, '1 h'),
    }),
    
    // File uploads
    upload: new Ratelimit({
      redis: this.redis,
      limiter: Ratelimit.slidingWindow(10, '1 h'),
    }),
  };
  
  // Check rate limit
  static async checkRateLimit(
    identifier: string,
    type: keyof typeof this.limiters = 'api'
  ): Promise<{ success: boolean; reset?: number; remaining?: number }> {
    const limiter = this.limiters[type];
    const result = await limiter.limit(identifier);
    
    return {
      success: result.success,
      reset: result.reset,
      remaining: result.remaining,
    };
  }
  
  // Brute force protection for login
  static async checkBruteForce(
    email: string,
    ip: string
  ): Promise<{ allowed: boolean; lockoutTime?: number }> {
    const emailKey = `bf:email:${email}`;
    const ipKey = `bf:ip:${ip}`;
    
    const [emailAttempts, ipAttempts] = await Promise.all([
      this.redis.get(emailKey),
      this.redis.get(ipKey),
    ]);
    
    // Block if too many attempts from same email or IP
    if (emailAttempts && emailAttempts > 10) {
      return { allowed: false, lockoutTime: 3600 }; // 1 hour
    }
    
    if (ipAttempts && ipAttempts > 50) {
      return { allowed: false, lockoutTime: 1800 }; // 30 minutes
    }
    
    return { allowed: true };
  }
  
  // Record failed login attempt
  static async recordFailedLogin(email: string, ip: string): Promise<void> {
    const emailKey = `bf:email:${email}`;
    const ipKey = `bf:ip:${ip}`;
    
    await Promise.all([
      this.redis.incr(emailKey),
      this.redis.incr(ipKey),
      this.redis.expire(emailKey, 3600), // 1 hour
      this.redis.expire(ipKey, 1800),    // 30 minutes
    ]);
  }
}
```

## SQL Injection Prevention

### Safe Database Queries
```typescript
import { prisma } from '@/lib/prisma';

export class SafeDatabaseOperations {
  // Safe user search with parameterized queries
  static async searchUsers(searchTerm: string, limit: number = 10) {
    // Prisma automatically parameterizes queries
    return prisma.user.findMany({
      where: {
        OR: [
          { email: { contains: searchTerm, mode: 'insensitive' } },
          { name: { contains: searchTerm, mode: 'insensitive' } },
        ],
      },
      take: limit,
      select: {
        id: true,
        email: true,
        name: true,
        createdAt: true,
      },
    });
  }
  
  // Safe dynamic filtering
  static async getFilteredUsers(filters: {
    role?: string;
    status?: string;
    createdAfter?: Date;
  }) {
    const where: any = {};
    
    // Build where clause safely
    if (filters.role) {
      where.role = filters.role;
    }
    
    if (filters.status) {
      where.status = filters.status;
    }
    
    if (filters.createdAfter) {
      where.createdAt = {
        gte: filters.createdAfter,
      };
    }
    
    return prisma.user.findMany({
      where,
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        status: true,
        createdAt: true,
      },
    });
  }
  
  // Safe raw query example (when absolutely necessary)
  static async performComplexQuery(userId: string) {
    // Use $queryRaw with parameterized queries
    return prisma.$queryRaw`
      SELECT u.*, COUNT(p.id) as post_count
      FROM users u
      LEFT JOIN posts p ON u.id = p.author_id
      WHERE u.id = ${userId}
      GROUP BY u.id
    `;
  }
}
```

## Authorization & Access Control

### Role-Based Access Control (RBAC)
```typescript
export enum Permission {
  READ_USERS = 'read:users',
  WRITE_USERS = 'write:users',
  DELETE_USERS = 'delete:users',
  READ_ADMIN = 'read:admin',
  WRITE_ADMIN = 'write:admin',
}

export enum Role {
  USER = 'user',
  MODERATOR = 'moderator',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin',
}

const rolePermissions: Record<Role, Permission[]> = {
  [Role.USER]: [Permission.READ_USERS],
  [Role.MODERATOR]: [
    Permission.READ_USERS,
    Permission.WRITE_USERS,
  ],
  [Role.ADMIN]: [
    Permission.READ_USERS,
    Permission.WRITE_USERS,
    Permission.DELETE_USERS,
    Permission.READ_ADMIN,
  ],
  [Role.SUPER_ADMIN]: Object.values(Permission),
};

export class AccessControl {
  // Check if user has permission
  static hasPermission(userRole: Role, permission: Permission): boolean {
    const permissions = rolePermissions[userRole];
    return permissions.includes(permission);
  }
  
  // Check multiple permissions
  static hasAllPermissions(userRole: Role, permissions: Permission[]): boolean {
    return permissions.every(permission => this.hasPermission(userRole, permission));
  }
  
  // Middleware for permission checking
  static requirePermission(permission: Permission) {
    return async (request: NextRequest) => {
      const session = await getServerSession(authOptions);
      
      if (!session?.user) {
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }
      
      if (!this.hasPermission(session.user.role, permission)) {
        return NextResponse.json(
          { error: 'Insufficient permissions' },
          { status: 403 }
        );
      }
      
      return null; // Allow request
    };
  }
}
```

## Security Headers & Configuration

### Security Headers Middleware
```typescript
export function setSecurityHeaders(response: NextResponse): NextResponse {
  // Content Security Policy
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://trusted-scripts.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https:",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://api.yourdomain.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "upgrade-insecure-requests",
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', csp);
  
  // Other security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  
  // HSTS for HTTPS
  if (process.env.NODE_ENV === 'production') {
    response.headers.set(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains; preload'
    );
  }
  
  return response;
}

// Security middleware
export function createSecurityMiddleware() {
  return async (request: NextRequest) => {
    const response = NextResponse.next();
    return setSecurityHeaders(response);
  };
}
```

## File Upload Security

### Secure File Upload Handling
```typescript
import { randomBytes } from 'crypto';
import path from 'path';

export class SecureFileUpload {
  private static allowedMimeTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'text/plain',
  ];
  
  private static maxFileSize = 10 * 1024 * 1024; // 10MB
  
  // Validate file
  static validateFile(file: File): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check file size
    if (file.size > this.maxFileSize) {
      errors.push('File size exceeds limit');
    }
    
    // Check MIME type
    if (!this.allowedMimeTypes.includes(file.type)) {
      errors.push('File type not allowed');
    }
    
    // Check file extension
    const extension = path.extname(file.name).toLowerCase();
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt'];
    if (!allowedExtensions.includes(extension)) {
      errors.push('File extension not allowed');
    }
    
    return {
      valid: errors.length === 0,
      errors,
    };
  }
  
  // Generate safe filename
  static generateSafeFilename(originalName: string): string {
    const extension = path.extname(originalName);
    const randomName = randomBytes(16).toString('hex');
    return `${randomName}${extension}`;
  }
  
  // Scan file for malware (placeholder for actual implementation)
  static async scanFile(fileBuffer: Buffer): Promise<boolean> {
    // Integrate with antivirus service like ClamAV
    // Return true if file is safe
    return true;
  }
}
```

## Development Standards

### Security Quality Checklist
- [ ] All user inputs validated and sanitized
- [ ] XSS prevention implemented
- [ ] CSRF protection enabled
- [ ] SQL injection prevention verified
- [ ] Authentication security implemented
- [ ] Authorization controls enforced
- [ ] Rate limiting configured
- [ ] Security headers set
- [ ] File upload security implemented
- [ ] Password security enforced
- [ ] Sensitive data encrypted
- [ ] Error messages don't leak information
- [ ] Security testing completed
- [ ] Dependencies scanned for vulnerabilities