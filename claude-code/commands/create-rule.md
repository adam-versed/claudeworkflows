# Create Technology Implementation Rules

Create concise, focused implementation rule files for specific technologies, frameworks, or patterns. These rule files provide guard rails for automated code generation by defining required patterns and anti-patterns.

## Behavior

When this command is invoked, follow this methodology to create technology-specific rule files:

### Step 1: Research and Analysis

1. **Use systematic research** to gather authoritative information about the specified technology
2. **Focus on implementation patterns** rather than installation or setup guides
3. **Prioritize sources** in this order:
   - Official documentation and best practices guides
   - Established style guides and conventions
   - Production-ready examples and case studies
   - Community-established patterns and anti-patterns

### Step 2: Create Rule File

Generate a focused rule file at `./.claude/rules/[technology].md` with this structure:

#### Required Sections:

1. **File Header**: Technology name and applicable file glob patterns
2. **Core Implementation Rules**: Essential patterns that MUST be followed
3. **Security Rules**: Security-specific implementation requirements
4. **Performance Rules**: Performance optimization patterns
5. **Error Handling Rules**: Standardized error handling approaches
6. **Anti-Patterns**: Clear examples of what NOT to do with ❌ indicators

#### Content Guidelines:

- **Focus on HOW to implement**, not what the technology is
- **Include code examples** for every rule
- **Use imperative language**: "Always", "Never", "MUST", "REQUIRED"
- **Provide context** for when rules apply
- **Remove installation/setup instructions** - focus purely on implementation
- **Use clear section headers** for easy reference

### Step 3: Structure Requirements

````markdown
# [Technology] Implementation Rules

**Applicable File Types**: `**/*.{ext1,ext2,ext3}`

## Core Implementation Rules

### Rule Category

Brief description of when this rule applies:

```language
// REQUIRED pattern example
code example here
```
````

## Security Rules

[Security-specific implementation requirements]

## Performance Rules

[Performance optimization patterns]

## Error Handling Rules

[Standardized error handling approaches]

## Anti-Patterns to Avoid

### ❌ Never Do This

```language
// BAD - explanation of why this is wrong
bad code example
```

### ✅ Always Do This Instead

```language
// GOOD - correct implementation
good code example
```

```

## Process

1. **Parse the technology/framework name** from $ARGUMENTS
2. **Research implementation patterns** for the specified technology
3. **Create the rule file** at `./.claude/rules/[technology].md`
4. **Focus on actionable rules** with code examples
5. **Include both patterns and anti-patterns** for comprehensive guidance
6. **Verify all code examples** are syntactically correct and follow best practices

## Example Usage

- `/create-rule react` - Creates React component implementation rules
- `/create-rule prisma` - Creates Prisma ORM implementation patterns
- `/create-rule nextjs api` - Creates Next.js API route implementation rules
- `/create-rule typescript` - Creates TypeScript coding standards and patterns

## Output Requirements

The generated rule file should:
- Be immediately actionable for code generation
- Include file type glob patterns for automatic application
- Focus on implementation rather than explanation
- Provide clear do's and don'ts
- Include security and performance considerations
- Be concise yet comprehensive for the specified technology

$ARGUMENTS
```
