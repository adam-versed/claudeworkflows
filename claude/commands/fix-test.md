# fix-test v0.2

**Mindset**: "Tests must pass" - Systematic test failure resolution with root cause analysis and comprehensive validation.

## Behavior

Systematic test failure resolution combining automated analysis with manual investigation for reliable test suite maintenance.

### Test Fix Strategy

- **Failure Analysis**: Test failure categorization and root cause identification
- **Environment Issues**: Test environment configuration and dependency problems
- **Flaky Test Resolution**: Non-deterministic test behavior identification and fixes
- **Test Data Issues**: Test data consistency and isolation problems
- **Code Changes Impact**: Application changes affecting existing tests
- **Test Quality Improvement**: Test reliability and maintainability enhancement

## Test Fix Framework (Analysis 30% | Investigation 25% | Implementation 30% | Validation 15%)

### Failure Analysis

- **Error Categorization**: Unit test, integration test, or end-to-end test failures
- **Failure Pattern**: Single failure, systematic failure, or intermittent failure
- **Environment Factors**: CI/CD pipeline, local environment, or production environment
- **Timing Issues**: Race conditions, timeouts, or sequence dependencies

### Root Cause Investigation

- **Code Change Analysis**: Recent changes affecting test behavior
- **Dependency Issues**: External service dependencies and mock configurations
- **Data State Problems**: Test data consistency and cleanup issues
- **Configuration Drift**: Environment configuration changes affecting tests

## Optional Flags

--c7: Use to understand common test failure patterns and fixes for your testing framework (e.g., async testing in Jest, fixture management in pytest, mocking strategies in Vitest)
--seq: Use for complex test failures - breaks down into 'analyze failure type', 'check recent changes', 'investigate test environment', 'fix root cause', 'prevent future recurrence'

## Output Requirements

- Test failure analysis with root cause identification
- Test fixes with improved reliability and maintainability
- Enhanced test environment configuration and data management
- Test quality improvements with flaky test elimination

$ARGUMENTS
