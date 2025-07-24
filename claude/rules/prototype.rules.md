# Rapid Prototyping Implementation Rules

## Core Principles
- Prioritize speed and iteration over perfection
- Use existing libraries and frameworks instead of building from scratch
- Mock external dependencies rather than implementing full integrations
- Focus on demonstrating core functionality

## Development Rules

### Library Selection
- Choose well-established component libraries with extensive pre-built components
- Prefer opinionated frameworks that provide structure out-of-the-box
- Use starter templates and boilerplates when available
- Leverage UI component libraries for rapid interface development

### Data Handling
- Use mock data and fixtures for all external service calls
- Implement data persistence with in-memory stores or local storage
- Create realistic test data that demonstrates all use cases
- Avoid complex database setup or migrations

### Implementation Focus
- Build only the essential features needed for demonstration
- Skip edge cases and error handling unless critical to the demo
- Use hardcoded values where configuration would slow development
- Implement happy path scenarios first

### Code Quality Standards
- Readable code over optimized code
- Comments explaining shortcuts taken and future improvements needed
- Clear separation between prototype code and potential production code
- Document all assumptions and limitations

### Testing Approach
- Run type checking and build compilation after each feature addition
- Use language-appropriate tools (TypeScript tsc, Python mypy, Go build, etc.)
- Fix all type errors and build failures before proceeding
- Perform quick smoke tests on critical user paths
- Validate core functionality through manual testing
- Document discovered issues for future fixes
- Automated test suites not required for prototypes

## Output Requirements
- Working prototype accessible with minimal setup (single command ideally)
- README with clear instructions for running the prototype
- List of shortcuts taken and production considerations
- Screenshots or recordings demonstrating key functionality