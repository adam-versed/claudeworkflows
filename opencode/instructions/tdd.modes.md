# Test-Driven Development Mode

**Purpose**: Systematic test-driven development with comprehensive test coverage and quality assurance

## Core Principles:

- Write tests before implementation code
- Every new feature starts with a failing test
- Tests define the specification and expected behavior
- Implementation should be minimal to pass tests
- Never alter or suppress test behaviour to achieve a pass
- Tests must run in under 10 seconds for development cycle
- Use test doubles (mocks, stubs) for external dependencies
- Assertions must be specific and provide clear failure messages

## Test Creation Standards:

- Test names must clearly describe the expected behavior
- Each test should verify one specific behavior
- Tests must be independent and runnable in any order
- Test use cases must be 100% unique, no duplication or overlapping of test effort

## Test Coverage Requirements:

- 100% coverage for business logic and critical paths, but not external libraries
- Edge cases and error scenarios must have explicit tests
- Integration tests for all external dependencies

## Implementation Process:

1. **Red Phase**: Write failing test that defines desired behavior
2. **Green Phase**: Write minimal code to make test pass
3. **Refactor Phase**: Improve code design while keeping tests green
4. **Repeat**: Continue cycle for each new requirement

## Test Types Required:

- **Unit Tests**: For all public methods and functions
- **Integration Tests**: For component interactions
- **Acceptance Tests**: For user-facing features
