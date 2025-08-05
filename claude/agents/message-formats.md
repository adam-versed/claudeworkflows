# Inter-Agent Message Formats

## Overview

This document defines standardized message formats for communication between agents in the build workflow system. All agents must use these formats to ensure consistent, traceable communication.

## Base Message Structure

All messages include these core fields:

```typescript
interface BaseMessage {
  messageId: string; // Unique identifier (UUID)
  correlationId: string; // Links related messages
  timestamp: string; // ISO 8601 format
  from: string; // Sending agent name
  to: string; // Receiving agent name
  type: MessageType; // Message type enum
  version: string; // Format version (currently "1.0")
}
```

## Message Types

### Task Assignment

```typescript
interface TaskAssignment extends BaseMessage {
  type: "TASK_ASSIGNMENT";
  payload: {
    taskId: string;
    title: string;
    description: string;
    phase: number;
    dependencies: string[];
    context: {
      approvedDesign?: string;
      existingDocs?: string[];
      constraints?: string[];
      planFile?: string; // Path to implementation plan if applicable
    };
  };
}
```

Example:

```json
{
  "messageId": "msg-123",
  "correlationId": "task-001",
  "timestamp": "2024-01-01T12:00:00Z",
  "from": "@agent-build-orchestrator",
  "to": "@agent-fullstack-developer",
  "type": "TASK_ASSIGNMENT",
  "version": "1.0",
  "payload": {
    "taskId": "TASK-001",
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google",
    "phase": 2,
    "dependencies": [],
    "context": {
      "approvedDesign": "Use NextAuth.js with Google provider",
      "existingDocs": ["docs/auth/oauth-guide.md"]
    }
  }
}
```

### CTO Review Example

```json
{
  "messageId": "msg-456",
  "correlationId": "project-review",
  "timestamp": "2024-01-01T12:00:00Z",
  "from": "@agent-cto",
  "to": "@agent-build-orchestrator",
  "type": "CODEBASE_REVIEW_REPORT",
  "version": "1.0",
  "payload": {
    "reviewType": "INITIAL_ASSESSMENT",
    "findings": {
      "architecture": {
        "status": "NEEDS_ATTENTION",
        "issues": ["Outdated dependencies", "Missing error boundaries"],
        "recommendations": ["Update to React 18", "Add global error handling"]
      },
      "documentation": {
        "gaps": ["API endpoints not documented"],
        "conflicts": ["README conflicts with package.json"],
        "outdated": ["docs/setup.md references old Node version"],
        "updated": ["docs/setup.md", "README.md"]
      }
    },
    "blockers": [],
    "readyForImplementation": true
  }
}
```

### Status Update

```typescript
interface StatusUpdate extends BaseMessage {
  type: "STATUS_UPDATE";
  payload: {
    taskId: string;
    status: "STARTED" | "PROGRESS" | "BLOCKED" | "COMPLETED" | "FAILED";
    progress?: number; // 0-100
    details?: string;
    blockers?: string[];
  };
}
```

### State Transition

```typescript
interface StateTransition extends BaseMessage {
  type: "STATE_TRANSITION";
  payload: {
    taskId: string;
    fromState: State;
    toState: State;
    reason: string;
    metadata?: Record<string, any>;
  };
}
```

### Validation Request

```typescript
interface ValidationRequest extends BaseMessage {
  type: "VALIDATION_REQUEST";
  payload: {
    taskId: string;
    validationType: "DESIGN" | "QUALITY" | "SECURITY" | "CODEBASE_REVIEW";
    subject: string;
    details: {
      approach?: string;
      files?: string[];
      changes?: string;
      planFile?: string; // Path to implementation plan file for codebase reviews
    };
  };
}
```

### Validation Response

```typescript
interface ValidationResponse extends BaseMessage {
  type: "VALIDATION_RESPONSE";
  payload: {
    taskId: string;
    decision: "APPROVED" | "REJECTED" | "CONDITIONAL";
    reasons: string[];
    conditions?: string[];
    suggestions?: string[];
  };
}
```

### Quality Report

```typescript
interface QualityReport extends BaseMessage {
  type: "QUALITY_REPORT";
  payload: {
    taskId: string;
    status: "PASSED" | "FAILED";
    gates: {
      name: string;
      status: "PASSED" | "FAILED" | "SKIPPED";
      details?: string;
    }[];
    failureCount: number;
    actions: string[];
  };
}
```

### Error Report

```typescript
interface ErrorReport extends BaseMessage {
  type: "ERROR_REPORT";
  payload: {
    taskId?: string;
    severity: "CRITICAL" | "ERROR" | "WARNING";
    count: number;
    errors: {
      timestamp: string;
      message: string;
      source?: string;
      stackTrace?: string;
    }[];
    pattern?: string;
  };
}
```

### Escalation Request

```typescript
interface EscalationRequest extends BaseMessage {
  type: "ESCALATION_REQUEST";
  payload: {
    taskId: string;
    escalationType: "CTO" | "HUMAN";
    reason: string;
    failureHistory: {
      agent: string;
      attempts: number;
      lastError: string;
    }[];
    context: Record<string, any>;
  };
}
```

### Commit Request

```typescript
interface CommitRequest extends BaseMessage {
  type: "COMMIT_REQUEST";
  payload: {
    taskId: string;
    approvalRef: string; // Reference to quality approval
    files: string[];
    commitMessage: string;
    metadata: {
      qualityGatesPassed: boolean;
      approvedBy: string;
      timestamp: string;
    };
  };
}
```

### Documentation Query

```typescript
interface DocumentationQuery extends BaseMessage {
  type: "DOC_QUERY";
  payload: {
    queryType: "SEARCH" | "VERIFY" | "REGISTER";
    topic: string;
    keywords: string[];
    context?: string;
  };
}
```

### Documentation Response

```typescript
interface DocumentationResponse extends BaseMessage {
  type: "DOC_RESPONSE";
  payload: {
    found: boolean;
    documents: {
      path: string;
      relevance: number; // 0-100
      topics: string[];
      lastUpdated: string;
    }[];
    recommendation: "USE_EXISTING" | "UPDATE_EXISTING" | "CREATE_NEW";
  };
}
```

### Codebase Review Report

```typescript
interface CodebaseReviewReport extends BaseMessage {
  type: "CODEBASE_REVIEW_REPORT";
  payload: {
    taskId?: string;
    reviewType: "INITIAL_ASSESSMENT" | "PRE_IMPLEMENTATION";
    findings: {
      architecture: {
        status: "GOOD" | "NEEDS_ATTENTION" | "CRITICAL";
        issues: string[];
        recommendations: string[];
      };
      documentation: {
        gaps: string[];
        conflicts: string[];
        outdated: string[];
        updated: string[];
      };
      codeQuality: {
        technicalDebt: string[];
        patterns: string[];
        dependencies: string[];
      };
    };
    blockers: string[];
    readyForImplementation: boolean;
  };
}
```

## Communication Patterns

### Request-Response Pattern

```typescript
// Request
{
  "messageId": "req-123",
  "correlationId": "task-001",
  "type": "VALIDATION_REQUEST",
  // ... rest of request
}

// Response
{
  "messageId": "res-456",
  "correlationId": "task-001",     // Same correlation ID
  "replyTo": "req-123",            // References request
  "type": "VALIDATION_RESPONSE",
  // ... rest of response
}
```

### Broadcast Pattern

```typescript
// For announcements to multiple agents
{
  "messageId": "broadcast-789",
  "from": "build-orchestrator",
  "to": "*",                       // All agents
  "type": "STATUS_UPDATE",
  "broadcast": true,
  // ... rest of message
}
```

### Event Pattern

```typescript
// For state changes and notifications
{
  "messageId": "event-321",
  "from": "plan-manager",
  "to": "build-orchestrator",
  "type": "STATE_TRANSITION",
  "event": true,
  // ... rest of message
}
```

## Error Handling

### Message Validation Error

```typescript
interface MessageError extends BaseMessage {
  type: "MESSAGE_ERROR";
  payload: {
    originalMessageId: string;
    errorType: "INVALID_FORMAT" | "UNKNOWN_TYPE" | "MISSING_FIELD";
    details: string;
  };
}
```

### Timeout Handling

- Request timeout: 5 minutes default
- Correlation timeout: 30 minutes
- Retry policy: 3 attempts with exponential backoff

## Message Queue Rules

1. **FIFO Processing**: Messages processed in order received
2. **Priority Handling**: ESCALATION > ERROR > VALIDATION > STATUS
3. **Deduplication**: Same messageId ignored if seen within 1 hour
4. **Persistence**: Messages logged for 30 days

## Correlation Best Practices

1. **Task Correlation**: All messages for a task share correlationId = taskId
2. **Conversation Threading**: Related exchanges use same correlationId
3. **Escalation Chains**: Maintain correlationId through escalations
4. **Error Correlation**: Error reports include original correlationId

## Implementation Example

```typescript
class MessageBuilder {
  static createTaskAssignment(
    from: string,
    to: string,
    task: Task,
  ): TaskAssignment {
    return {
      messageId: generateUUID(),
      correlationId: task.id,
      timestamp: new Date().toISOString(),
      from,
      to,
      type: "TASK_ASSIGNMENT",
      version: "1.0",
      payload: {
        taskId: task.id,
        title: task.title,
        description: task.description,
        phase: task.phase,
        dependencies: task.dependencies,
        context: task.context,
      },
    };
  }
}
```

## Logging Format

All messages logged with structure:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "direction": "SENT" | "RECEIVED",
  "agent": "agent-name",
  "message": { /* full message */ },
  "processingTime": 150,  // milliseconds
  "result": "SUCCESS" | "ERROR"
}
```

## Version Migration

Current version: 1.0

Future versions must:

1. Maintain backward compatibility
2. Include version in all messages
3. Support version negotiation
4. Document migration path

Remember: Consistent message formats enable reliable inter-agent communication and system debugging.
