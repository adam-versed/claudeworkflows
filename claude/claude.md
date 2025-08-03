## Monitor User Request For Flags

**When a `--[FLAG]` flag(s) is present in the user request, follow the matching condition**:

<condition>

- If user request contains flag `--prototype` then <rapid_prototype_rules> = enabled
- If user request contains flag `--tdd` then <tdd> = enabled
- if user request contains flag `--seq` then use the sequential-thinking MCP tool for complex, multi-step analysis
- if user request contains flag `--gitgrep` then use the grep MCP tool to search across highly rated GitHub repositories for code examples or libraries to use

</condition>

<rapid_prototyping_rules>

`--prototype` **When this flag is used**: Follow prototype implementation rules below

**Purpose**

Quick proof-of-concept development with minimal setup and rapid iteration

**Core Principles:**

- Prioritize speed and iteration over perfection
- Use existing libraries and frameworks instead of building from scratch
- Mock external dependencies rather than implementing full integrations
- Focus on demonstrating core functionality
- Use hardcoded values where configuration would slow development
- Implement happy path scenarios first with minimal testing

**Library Selection:**

- Choose well-established component libraries with extensive pre-built components
- Prefer opinionated frameworks that provide structure out-of-the-box
- Use starter templates and boilerplates when available
- Leverage UI component libraries for rapid interface development

**Data Handling:**

- Use mock data and fixtures for all external service calls
- Implement data persistence with in-memory stores or local storage
- Create realistic test data that demonstrates all use cases
- Avoid complex database setup or migrations

**Testing Approach:**

- Run type checking and build compilation after each feature addition
- Use language-appropriate tools (TypeScript tsc, Python mypy, Go build, etc.)
- Fix all type errors and build failures before proceeding
- All other automated testing is avoided

**Output Requirements:**

- Working prototype accessible with minimal setup (single command ideally)

</rapid_prototyping_rules>

<tdd_rules>

`--tdd` **When this flag is used**: Follow test-driven development implementation rules below

**Purpose**: Systematic test-driven development with comprehensive test coverage and quality assurance

**Core Principles:**

- Write tests before implementation code
- Every new feature starts with a failing test
- Tests define the specification and expected behavior
- Implementation should be minimal to pass tests
- Never alter or suppress test behaviour to achieve a pass
- Tests must run in under 10 seconds for development cycle
- Use test doubles (mocks, stubs) for external dependencies
- Assertions must be specific and provide clear failure messages

**Test Creation Standards:**

- Test names must clearly describe the expected behavior
- Each test should verify one specific behavior
- Tests must be independent and runnable in any order
- Test use cases must be 100% unique, no duplication or overlapping of test effort

**Test Coverage Requirements:**

- 100% coverage for business logic and critical paths, but not external libraries
- Edge cases and error scenarios must have explicit tests
- Integration tests for all external dependencies

**Implementation Process:**

1. **Red Phase**: Write failing test that defines desired behavior
2. **Green Phase**: Write minimal code to make test pass
3. **Refactor Phase**: Improve code design while keeping tests green
4. **Repeat**: Continue cycle for each new requirement

**Test Types Required:**

- **Unit Tests**: For all public methods and functions
- **Integration Tests**: For component interactions
- **Acceptance Tests**: For user-facing features

</tdd_rules>
