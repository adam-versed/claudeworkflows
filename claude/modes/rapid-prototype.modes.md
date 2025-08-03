# Rapid Prototyping Mode

**Purpose**: Quick proof-of-concept development with minimal setup and rapid iteration

## Core Principles:

- Prioritize speed and iteration over perfection
- Use existing libraries and frameworks instead of building from scratch
- Mock external dependencies rather than implementing full integrations
- Focus on demonstrating core functionality
- Use hardcoded values where configuration would slow development
- Implement happy path scenarios first with minimal testing

## Library Selection:

- Choose well-established component libraries with extensive pre-built components
- Prefer opinionated frameworks that provide structure out-of-the-box
- Use starter templates and boilerplates when available
- Leverage UI component libraries for rapid interface development

## Data Handling:

- Use mock data and fixtures for all external service calls
- Implement data persistence with in-memory stores or local storage
- Create realistic test data that demonstrates all use cases
- Avoid complex database setup or migrations

## Testing Approach:

- Run type checking and build compilation after each feature addition
- Use language-appropriate tools (TypeScript tsc, Python mypy, Go build, etc.)
- Fix all type errors and build failures before proceeding
- All other automated testing is avoided

## Output Requirements:

- Working prototype accessible with minimal setup (single command ideally)
