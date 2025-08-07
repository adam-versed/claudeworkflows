# Testing Development Rules

## Testing Strategy Framework

### Test Level Responsibilities

```yaml
# Clear separation of test concerns for 90% unique coverage

unit_tests:
  responsibility: "Business logic, pure functions, component behavior"
  coverage_focus:
    - Algorithm correctness
    - Edge case handling
    - State transitions
    - Input validation logic
    - Error boundary behavior
  avoid_testing:
    - API calls (mock these)
    - Database operations (mock these)
    - Browser-specific behavior
    - Third-party library internals

integration_tests:
  responsibility: "Service interactions, API contracts, data flow"
  coverage_focus:
    - API endpoint behavior
    - Database operations
    - External service integration
    - Authentication/authorization
    - Cross-service communication
  avoid_testing:
    - UI interactions (leave to E2E)
    - Pure business logic (covered in unit tests)
    - Library behavior (assume tested)

e2e_tests:
  responsibility: "Critical user journeys, browser behavior, full system"
  coverage_focus:
    - Core user workflows
    - Cross-browser compatibility
    - UI interaction patterns
    - End-to-end data flow
    - Real-world scenarios
  avoid_testing:
    - Every possible user path (focus on critical paths)
    - Edge cases covered in unit tests
    - API-only scenarios (covered in integration tests)
```

## Unit Testing Patterns

### Business Logic Testing

```typescript
import { describe, it, expect, beforeEach, vi } from "vitest";
import { UserValidator } from "@/services/user-validator";
import { PriceCalculator } from "@/services/price-calculator";

describe("UserValidator", () => {
  let validator: UserValidator;

  beforeEach(() => {
    validator = new UserValidator();
  });

  describe("validateEmail", () => {
    // Test business logic, not library behavior
    it("should validate complex email formats", () => {
      const validEmails = [
        "user+tag@example.com",
        "user.name@example.co.uk",
        "user123@example-site.com",
      ];

      validEmails.forEach((email) => {
        expect(validator.validateEmail(email)).toBe(true);
      });
    });

    it("should reject business-specific invalid formats", () => {
      const invalidEmails = [
        "user@tempmail.com", // Blocked domain
        "admin@company.com", // Reserved username
        "test@test.test", // Test domains blocked
      ];

      invalidEmails.forEach((email) => {
        expect(validator.validateEmail(email)).toBe(false);
      });
    });

    it("should handle edge cases in email validation", () => {
      expect(validator.validateEmail("")).toBe(false);
      expect(validator.validateEmail("a".repeat(256))).toBe(false);
      expect(validator.validateEmail("user@")).toBe(false);
    });
  });
});

describe("PriceCalculator", () => {
  let calculator: PriceCalculator;

  beforeEach(() => {
    calculator = new PriceCalculator();
  });

  it("should calculate tiered pricing correctly", () => {
    // Test complex business logic
    const items = [
      { quantity: 5, unitPrice: 100 }, // 5% discount
      { quantity: 15, unitPrice: 50 }, // 10% discount
      { quantity: 25, unitPrice: 20 }, // 15% discount
    ];

    const result = calculator.calculateTotal(items);

    expect(result).toEqual({
      subtotal: 1475,
      discount: 160,
      total: 1315,
      discountRate: 0.108, // Weighted average
    });
  });

  it("should handle quantity-based discount tiers", () => {
    const testCases = [
      { quantity: 1, expected: 0 },
      { quantity: 10, expected: 0.05 },
      { quantity: 50, expected: 0.1 },
      { quantity: 100, expected: 0.15 },
    ];

    testCases.forEach(({ quantity, expected }) => {
      expect(calculator.getDiscountRate(quantity)).toBe(expected);
    });
  });
});
```

### Component Testing

```tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { UserProfile } from "@/components/UserProfile";

// Test utilities
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("UserProfile Component", () => {
  // Focus on component behavior, not API calls
  it("should render different states based on props", () => {
    const scenarios = [
      {
        props: { user: null, loading: true },
        expected: "Loading...",
      },
      {
        props: { user: null, loading: false, error: "Not found" },
        expected: "User not found",
      },
      {
        props: { user: mockUser, loading: false },
        expected: mockUser.name,
      },
    ];

    scenarios.forEach(({ props, expected }) => {
      render(<UserProfile {...props} />);
      expect(screen.getByText(expected)).toBeInTheDocument();
    });
  });

  it("should handle edit mode transitions", () => {
    const onUpdate = vi.fn();

    render(<UserProfile user={mockUser} onUpdate={onUpdate} />);

    // Test state transitions
    expect(screen.getByText("Edit")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Edit"));
    expect(screen.getByText("Cancel")).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toBeInTheDocument();
  });
});
```

## Integration Testing Patterns

### API Integration Testing

```typescript
import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import request from "supertest";
import { app } from "@/app";
import { db } from "@/lib/db";
import { createTestUser, clearDatabase } from "@/test/helpers";

describe("User API Integration", () => {
  beforeAll(async () => {
    await db.migrate.latest();
  });

  afterAll(async () => {
    await db.destroy();
  });

  beforeEach(async () => {
    await clearDatabase();
  });

  describe("POST /api/users", () => {
    it("should create user with proper data persistence", async () => {
      const userData = {
        email: "test@example.com",
        password: "SecurePass123!",
        name: "Test User",
      };

      const response = await request(app)
        .post("/api/users")
        .send(userData)
        .expect(201);

      // Verify API response
      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: userData.email,
        name: userData.name,
      });
      expect(response.body.password).toBeUndefined();

      // Verify database persistence
      const dbUser = await db("users").where({ email: userData.email }).first();
      expect(dbUser).toBeTruthy();
      expect(dbUser.password).not.toBe(userData.password); // Should be hashed
      expect(dbUser.created_at).toBeTruthy();
    });

    it("should enforce unique email constraint", async () => {
      const existingUser = await createTestUser();

      const response = await request(app)
        .post("/api/users")
        .send({
          email: existingUser.email,
          password: "Different123!",
          name: "Different Name",
        })
        .expect(409);

      expect(response.body.error).toBe("Email already registered");

      // Verify no duplicate was created
      const userCount = await db("users")
        .where({ email: existingUser.email })
        .count("* as count");
      expect(userCount[0].count).toBe(1);
    });

    it("should handle database transaction rollback", async () => {
      // Mock email service to fail
      const emailService = await import("@/services/email");
      vi.spyOn(emailService, "sendWelcomeEmail").mockRejectedValue(
        new Error("Email service down"),
      );

      await request(app)
        .post("/api/users")
        .send({
          email: "test@example.com",
          password: "SecurePass123!",
          name: "Test User",
        })
        .expect(500);

      // Verify user was not created due to transaction rollback
      const dbUser = await db("users")
        .where({ email: "test@example.com" })
        .first();
      expect(dbUser).toBeFalsy();
    });
  });

  describe("Authentication Flow", () => {
    it("should handle complete login flow", async () => {
      const user = await createTestUser();

      // Test login
      const loginResponse = await request(app)
        .post("/api/auth/login")
        .send({
          email: user.email,
          password: "password123",
        })
        .expect(200);

      expect(loginResponse.body.token).toBeTruthy();

      // Test authenticated request
      const profileResponse = await request(app)
        .get(`/api/users/${user.id}`)
        .set("Authorization", `Bearer ${loginResponse.body.token}`)
        .expect(200);

      expect(profileResponse.body.email).toBe(user.email);
    });

    it("should handle token expiration", async () => {
      const expiredToken = generateExpiredToken();

      await request(app)
        .get("/api/users/profile")
        .set("Authorization", `Bearer ${expiredToken}`)
        .expect(401);
    });
  });
});
```

### Service Integration Testing

```typescript
describe("Payment Processing Integration", () => {
  it("should handle complete payment flow", async () => {
    const user = await createTestUser();
    const product = await createTestProduct();

    // Create order
    const orderResponse = await request(app)
      .post("/api/orders")
      .set("Authorization", await getAuthToken(user))
      .send({
        items: [{ productId: product.id, quantity: 2 }],
        paymentMethod: "test_card",
      })
      .expect(201);

    const orderId = orderResponse.body.id;

    // Verify order status progression
    let order = await db("orders").where({ id: orderId }).first();
    expect(order.status).toBe("pending");

    // Process payment (this would trigger webhook in real scenario)
    await request(app)
      .post(`/api/orders/${orderId}/process-payment`)
      .set("Authorization", await getAdminToken())
      .expect(200);

    // Verify order completion
    order = await db("orders").where({ id: orderId }).first();
    expect(order.status).toBe("completed");

    // Verify inventory update
    const updatedProduct = await db("products")
      .where({ id: product.id })
      .first();
    expect(updatedProduct.stock).toBe(product.stock - 2);
  });
});
```

## E2E Testing Patterns

### Critical User Journey Testing

```typescript
import { test, expect } from "@playwright/test";
import { createTestUser, loginAs, clearDatabase } from "@/test/e2e-helpers";

test.describe("Critical User Journeys", () => {
  test.beforeEach(async ({ page }) => {
    await clearDatabase();
  });

  test("Complete user registration and onboarding flow", async ({ page }) => {
    // This is a critical path that must work end-to-end
    await page.goto("/register");

    // Registration
    await page.fill('[name="email"]', "newuser@example.com");
    await page.fill('[name="password"]', "SecurePass123!");
    await page.fill('[name="confirmPassword"]', "SecurePass123!");
    await page.fill('[name="firstName"]', "New");
    await page.fill('[name="lastName"]', "User");
    await page.check('[name="acceptTerms"]');

    await page.click('button[type="submit"]');

    // Email verification step
    await expect(page.locator("text=Check your email")).toBeVisible();

    // Simulate email verification
    const verificationLink = await getVerificationLinkFromTestEmail(
      "newuser@example.com",
    );
    await page.goto(verificationLink);

    // Onboarding flow
    await expect(
      page.locator("text=Welcome! Let's set up your profile"),
    ).toBeVisible();

    await page.fill('[name="company"]', "Test Company");
    await page.selectOption('[name="role"]', "developer");
    await page.click('button:text("Complete Setup")');

    // Should be redirected to dashboard
    await page.waitForURL("/dashboard");
    await expect(page.locator("text=Welcome, New!")).toBeVisible();

    // Verify user can access protected features
    await page.click("text=My Profile");
    await expect(page.locator("text=New User")).toBeVisible();
  });

  test("Complete purchase flow for returning customer", async ({ page }) => {
    // Another critical business flow
    const user = await createTestUser();
    await loginAs(page, user);

    // Browse products
    await page.goto("/products");
    await page.click('[data-testid="product-card"]:first-child');

    // Add to cart
    await page.selectOption('[name="quantity"]', "2");
    await page.click('button:text("Add to Cart")');

    // Verify cart update
    await expect(page.locator('[data-testid="cart-count"]')).toHaveText("2");

    // Proceed to checkout
    await page.click('[data-testid="cart-button"]');
    await page.click('button:text("Checkout")');

    // Fill shipping information
    await page.fill('[name="address"]', "123 Test St");
    await page.fill('[name="city"]', "Test City");
    await page.selectOption('[name="state"]', "CA");
    await page.fill('[name="zipCode"]', "12345");

    await page.click('button:text("Continue to Payment")');

    // Payment (using test card)
    await page.fill('[name="cardNumber"]', "4242424242424242");
    await page.fill('[name="expiry"]', "1225");
    await page.fill('[name="cvc"]', "123");

    await page.click('button:text("Place Order")');

    // Order confirmation
    await expect(page.locator("text=Order Confirmed")).toBeVisible();
    await expect(page.locator('[data-testid="order-number"]')).toBeVisible();

    // Verify order in history
    await page.click("text=View Order History");
    await expect(
      page.locator('[data-testid="order-row"]:first-child'),
    ).toBeVisible();
  });
});
```

### Cross-Browser Testing

```typescript
test.describe("Cross-Browser Critical Functionality", () => {
  ["chromium", "firefox", "webkit"].forEach((browserName) => {
    test(`Core functionality works in ${browserName}`, async ({ page }) => {
      // Only test core functionality across browsers, not every feature
      const user = await createTestUser();

      await page.goto("/login");
      await page.fill('[name="email"]', user.email);
      await page.fill('[name="password"]', "password123");
      await page.click('button[type="submit"]');

      await page.waitForURL("/dashboard");
      await expect(page.locator("text=Dashboard")).toBeVisible();

      // Test one core feature works
      await page.click("text=My Profile");
      await expect(page.locator("text=Edit Profile")).toBeVisible();
    });
  });
});
```

## Security Testing Patterns

### Authentication Security Testing

```typescript
describe("Security Testing", () => {
  describe("Authentication Security", () => {
    it("should prevent brute force attacks", async () => {
      const attempts = [];

      // Make 10 rapid failed login attempts
      for (let i = 0; i < 10; i++) {
        attempts.push(
          request(app).post("/api/auth/login").send({
            email: "test@example.com",
            password: "wrongpassword",
          }),
        );
      }

      const responses = await Promise.all(attempts);

      // Should be rate limited
      const rateLimited = responses.filter((r) => r.status === 429);
      expect(rateLimited.length).toBeGreaterThan(0);
    });

    it("should not leak user existence information", async () => {
      // Test with non-existent user
      const response1 = await request(app).post("/api/auth/login").send({
        email: "nonexistent@example.com",
        password: "password",
      });

      // Test with existing user, wrong password
      const existingUser = await createTestUser();
      const response2 = await request(app).post("/api/auth/login").send({
        email: existingUser.email,
        password: "wrongpassword",
      });

      // Both should return same error message and timing
      expect(response1.status).toBe(401);
      expect(response2.status).toBe(401);
      expect(response1.body.error).toBe(response2.body.error);
    });
  });
});
```

### Input Validation Security Testing

```typescript
describe("Input Validation Security", () => {
  it("should prevent SQL injection in search", async () => {
    const maliciousQueries = [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "'; SELECT * FROM users WHERE '1'='1",
    ];

    for (const query of maliciousQueries) {
      const response = await request(app)
        .get("/api/search")
        .query({ q: query })
        .set("Authorization", await getAuthToken());

      // Should not fail catastrophically
      expect(response.status).toBeLessThan(500);

      // Should not return all users (sign of successful injection)
      if (response.status === 200) {
        expect(response.body.results.length).toBeLessThan(100);
      }
    }
  });

  it("should sanitize HTML input", async () => {
    const xssPayloads = [
      '<script>alert("xss")</script>',
      '<img src=x onerror=alert("xss")>',
      '<svg onload=alert("xss")>',
      'javascript:alert("xss")',
    ];

    const user = await createTestUser();
    const token = await getAuthToken(user);

    for (const payload of xssPayloads) {
      const response = await request(app)
        .patch(`/api/users/${user.id}`)
        .set("Authorization", token)
        .send({ bio: payload })
        .expect(200);

      // Verify XSS payload was sanitized
      expect(response.body.bio).not.toContain("<script>");
      expect(response.body.bio).not.toContain("javascript:");
      expect(response.body.bio).not.toContain("onerror");
      expect(response.body.bio).not.toContain("onload");
    }
  });
});
```

## Testing Quality Standards

### Coverage Requirements

```yaml
quality_gates:
  unit_tests:
    min_coverage: 90%
    max_execution_time: "2 minutes"
    focus: "Business logic only"

  integration_tests:
    api_coverage: 100%
    max_execution_time: "2 minutes"
    focus: "Service interactions only"

  e2e_tests:
    critical_paths: "All major user journeys"
    max_execution_time: "3 minutes"
    focus: "Real user scenarios only"

  performance_tests:
    load_capacity: "Expected user volume"
    response_times: "p95 < 200ms for APIs"

  security_tests:
    owasp_top_10: "All vulnerabilities tested"
    auth_security: "All auth flows secured"
```

### Test Efficiency Metrics

- **Test Execution Time**: Complete suite under 5 minutes
- **Test Reliability**: 99% pass rate on repeat runs
- **Coverage Uniqueness**: <10% duplicate coverage across levels
- **Test Maintenance**: Tests should not break with refactoring

## Development Standards

### Testing Quality Checklist

- [ ] 90% unique coverage achieved across all test levels
- [ ] No redundant tests between unit/integration/E2E
- [ ] All bespoke business logic covered in unit tests
- [ ] All API contracts validated in integration tests
- [ ] Critical user journeys covered in E2E tests
- [ ] Security vulnerabilities tested with real attack vectors
- [ ] Performance benchmarks meet requirements
- [ ] Test suite executes in under 5 minutes
- [ ] Tests are reliable and maintainable
- [ ] Focus on high-value, high-risk scenarios
