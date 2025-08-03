# Command Workflow Test Examples

Copy and paste these commands into Claude Code terminal to test the workflows:

## Security Analysis

```
/analyze-security check the project in test_codebase for hardcoded secrets and vulnerabilities
```

## Code Quality Analysis

```
/analyze-code-quality review the code in test_codebase and identify complexity issues
```

## Architecture Analysis

```
/analyze-architecture evaluate the design patterns and scalability of test_codebase
```

## Performance Analysis

```
/analyze-performance identify bottlenecks and optimization opportunities in test_codebase
```

## Root Cause Analysis

```
/analyze-root-cause investigate potential issues and trace execution patterns in test_codebase
```

## Bug Fixing

```
/fix-bug debug the authentication issue in test_codebase where login fails
```

## Performance Fixing

```
/fix-performance optimize the slow database queries in test_codebase
```

## Refactoring Planning

```
/plan-refactor migrate the project in test_codebase to use modern patterns and improve maintainability
```

## Solution Planning

```
/plan-solution design a new user authentication system for the project in test_codebase
```

## Expected Behavior

Each command should:

1. Use Glob tool to find script paths dynamically
2. Execute scripts with `--output-format json`
3. Display analysis results with findings and recommendations
4. Show proper error handling if scripts fail
5. Demonstrate the LLM script path locator approach working correctly
