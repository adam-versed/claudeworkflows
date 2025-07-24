# Test-Driven Development Implementation Rules

## Core Principles

- Write tests before implementation code
- Tests define the specification and expected behavior
- Implementation should be minimal to pass tests
- Refactor only after tests are green

## Development Rules

### Test Creation Standards

- Every new feature starts with a failing test
- Test names must clearly describe the expected behavior
- Each test should verify one specific behavior
- Tests must be independent and runnable in any order

### Test Coverage Requirements

- Minimum 80% code coverage for all new code
- 100% coverage for business logic and critical paths, but not external libraries
- Edge cases and error scenarios must have explicit tests
- Integration tests for all external dependencies

### Implementation Process

1. **Red Phase**: Write failing test that defines desired behavior
2. **Green Phase**: Write minimal code to make test pass
3. **Refactor Phase**: Improve code design while keeping tests green
4. **Repeat**: Continue cycle for each new requirement

### Code Implementation Rules

- No production code without a failing test
- Implementation must be the simplest solution that passes tests
- Duplication is acceptable until third occurrence (Rule of Three)
- Refactoring must not change external behavior

### Test Types Required

- **Unit Tests**: For all public methods and functions
- **Integration Tests**: For component interactions
- **Acceptance Tests**: For user-facing features
- **Performance Tests**: For critical paths with SLA requirements

### Quality Standards

- Tests must run in under 10 seconds for development cycle
- Test code must be as clean and maintainable as production code
- Use test doubles (mocks, stubs) for external dependencies
- Assertions must be specific and provide clear failure messages

## Output Requirements

- Full test suite with all tests passing
- Test coverage report showing minimum thresholds met
- Documentation of test scenarios and acceptance criteria
- CI/CD configuration for automated test execution
