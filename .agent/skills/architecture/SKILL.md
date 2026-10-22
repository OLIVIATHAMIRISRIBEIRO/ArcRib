---
name: architecture
description: "System design patterns, DDD, 12-Factor App, SOLID principles, event-driven architecture, and architectural decision frameworks"
triggers: [context, architecture, design, system]
---

# Architecture Skill

> **Purpose**: Apply proven architectural patterns for scalable, maintainable systems using industry-standard methodologies

---

## Overview

This skill provides deep guidance for designing software architectures using Domain-Driven Design, Clean Architecture, the 12-Factor App methodology, event-driven patterns, and SOLID principles.

---

## Architectural Patterns

### 1. Layered Architecture

```
┌─────────────────────────┐
│    Presentation Layer   │  ← Controllers, Views, API endpoints
├─────────────────────────┤
│    Application Layer    │  ← Use Cases, Services, Orchestration
├─────────────────────────┤
│      Domain Layer       │  ← Entities, Business Logic, Domain Events
├─────────────────────────┤
│   Infrastructure Layer  │  ← Database, External APIs, Messaging
└─────────────────────────┘
```

**Rule**: Each layer ONLY imports from the layer directly below it. Never skip layers.

### 2. Clean Architecture

```
                ┌─────────────┐
                │  Frameworks  │  ← Web, DB, UI (outermost)
              ┌─┤             ├─┐
              │ │  Adapters   │ │  ← Controllers, Gateways, Presenters
            ┌─┤ │             │ ├─┐
            │ │ │  Use Cases  │ │ │  ← Application business rules
          ┌─┤ │ │             │ │ ├─┐
          │ │ │ │  Entities   │ │ │ │  ← Core business objects (innermost)
          └─┤ │ │             │ │ ├─┘
            └─┤ │             │ ├─┘
              └─┤             ├─┘
                └─────────────┘
```

**Dependency Rule**: Source code dependencies ALWAYS point inward. Inner layers know nothing about outer layers.

### 3. Hexagonal Architecture (Ports & Adapters)

```
         ┌─────────────────┐
   ──────│     Ports       │──────
   Input │   (Interfaces)  │ Output
   Ports │                 │ Ports
         │  Domain Core    │
         │                 │
   ──────│    Adapters     │──────
   Input │  (Implementations)│ Output
   Adapters                  Adapters
         └─────────────────┘
```

**Key Insight**: The domain core defines ports (interfaces). Adapters implement them. This makes the domain testable without infrastructure.

---

## Domain-Driven Design (DDD)

### Strategic DDD — Bounded Contexts

| Concept | Definition | Example |
|:--------|:-----------|:--------|
| **Bounded Context** | A boundary within which a domain model is consistent | "Order" means different things in Sales vs Shipping |
| **Ubiquitous Language** | Shared vocabulary within a bounded context | "Customer" in Sales = "Recipient" in Shipping |
| **Context Map** | Visual map of relationships between bounded contexts | Sales ← Customer/Supplier → Fulfillment |
| **Anti-Corruption Layer** | Translation layer between contexts with different models | Adapter that maps external API models to domain models |

### Tactical DDD — Building Blocks

| Building Block | Purpose | Rules |
|:--------------|:--------|:------|
| **Entity** | Object with identity that persists over time | Has unique ID, mutable state, lifecycle |
| **Value Object** | Immutable object defined by its attributes | No ID, compared by value, always valid |
| **Aggregate** | Cluster of entities with a root that enforces invariants | External access only through root, transactional consistency |
| **Repository** | Interface for aggregate persistence | One per aggregate, hides storage details |
| **Domain Service** | Stateless logic spanning multiple aggregates | When logic doesn't belong to a single entity |
| **Domain Event** | Record of something that happened in the domain | Immutable, past tense (OrderPlaced, PaymentReceived) |
| **Factory** | Complex object/aggregate creation | Encapsulates creation logic and invariant enforcement |

### Aggregate Design Rules

1. **Protect invariants within aggregate boundaries** — All business rules enforced by the aggregate root
2. **Reference other aggregates by ID only** — Never hold direct object references across aggregate boundaries
3. **One transaction per aggregate** — Don't modify multiple aggregates in a single transaction
4. **Design small aggregates** — Smaller = less contention, better scalability
5. **Use eventual consistency between aggregates** — Domain events for cross-aggregate communication

---

## 12-Factor App Methodology

| Factor | Principle | Implementation |
|:-------|:----------|:--------------|
| **I. Codebase** | One codebase tracked in VCS, many deploys | Git repo, branches for environments |
| **II. Dependencies** | Explicitly declare and isolate dependencies | `package.json` + lockfile, no global installs |
| **III. Config** | Store config in the environment | `process.env.*`, never in code |
| **IV. Backing Services** | Treat backing services as attached resources | Database URL as environment variable |
| **V. Build, Release, Run** | Strictly separate build and run stages | CI builds artifact → deploy artifact → run |
| **VI. Processes** | Execute the app as stateless processes | No sticky sessions, no in-memory state between requests |
| **VII. Port Binding** | Export services via port binding | `app.listen(PORT)`, no container-specific coupling |
| **VIII. Concurrency** | Scale out via the process model | Horizontal scaling, not bigger machines |
| **IX. Disposability** | Maximize robustness with fast startup and graceful shutdown | `SIGTERM` handler, connection draining |
| **X. Dev/Prod Parity** | Keep development, staging, and production as similar as possible | Same database, same services, Docker |
| **XI. Logs** | Treat logs as event streams | Write to stdout, let platform aggregate |
| **XII. Admin Processes** | Run admin/management tasks as one-off processes | Database migrations, data fixes as scripts |

---

## Event-Driven Architecture

### Pattern Selection

| Pattern | Use When | Complexity | Consistency |
|:--------|:---------|:-----------|:-----------|
| **Request/Response** | Synchronous, simple operations | Low | Strong |
| **Event Notification** | Inform other services something happened | Low | Eventual |
| **Event-Carried State Transfer** | Share data without coupling to source | Medium | Eventual |
| **Event Sourcing** | Full audit trail, state reconstruction | High | Strong (per aggregate) |
| **CQRS** | Different read/write models needed | Medium-High | Eventual (between models) |

### Event Design Principles

1. **Events are facts** — Something that happened (past tense: `OrderPlaced`, not `PlaceOrder`)
2. **Events are immutable** — Never modify or delete events
3. **Events carry sufficient data** — Include everything consumers need (avoid callbacks)
4. **Events have schemas** — Version and validate event structures
5. **Events are ordered within an aggregate** — Global ordering is optional and expensive

---

## Design Principles

### SOLID — Applied

| Principle | Description | Violation Smell | Fix |
|:----------|:-----------|:---------------|:----|
| **S**ingle Responsibility | One reason to change | Class does file I/O AND business logic | Split into Repository + Service |
| **O**pen/Closed | Open for extension, closed for modification | `if/else` chain for new types | Strategy pattern, polymorphism |
| **L**iskov Substitution | Subtypes must be substitutable | Subclass throws unexpected exception | Respect base class contract |
| **I**nterface Segregation | Many specific interfaces | God interface with 20 methods | Split into focused interfaces |
| **D**ependency Inversion | Depend on abstractions | Service directly imports Prisma client | Inject Repository interface |

### Additional Principles

- **DRY**: Don't Repeat Yourself — Extract shared logic, but avoid premature abstraction
- **KISS**: Keep It Simple — Prefer straightforward solutions over clever ones
- **YAGNI**: You Aren't Gonna Need It — Don't build for hypothetical future requirements

---

## Module Structure (DDD-Aligned)

```
src/
├── domain/               # Core business logic (no framework imports)
│   ├── entities/         # Entities with identity
│   ├── value-objects/    # Immutable value types
│   ├── events/           # Domain events
│   ├── services/         # Domain services
│   └── repositories/     # Repository interfaces (ports)
├── application/          # Use cases / application services
│   ├── commands/         # Write operations
│   ├── queries/          # Read operations
│   └── handlers/         # Command/query handlers
├── infrastructure/       # External concerns (adapters)
│   ├── database/         # Repository implementations
│   ├── messaging/        # Event bus, message queues
│   ├── external-apis/    # Third-party integrations
│   └── config/           # Environment configuration
└── interfaces/           # Entry points (driving adapters)
    ├── http/             # REST/GraphQL controllers
    ├── events/           # Event consumers
    └── cli/              # CLI commands
```

---

## Architecture Decision Records (ADRs)

### When to Write an ADR

- Choosing between architectural approaches (monolith vs microservices)
- Selecting a technology (PostgreSQL vs MongoDB)
- Establishing a pattern (event sourcing vs CRUD)
- Making a trade-off (consistency vs availability)

### ADR Template

```markdown
# ADR-NNN: [Decision Title]

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXX
**Date**: YYYY-MM-DD
**Context**: [What is the issue? What constraints exist?]
**Decision**: [What was decided?]
**Consequences**: [What are the trade-offs? What becomes easier/harder?]
**Alternatives Considered**: [What was rejected and why?]
```

---

## Quick Reference

| Pattern | When to Use |
|:--------|:-----------|
| Monolith | MVP, small team, simple domain |
| Modular Monolith | Growing team, clear bounded contexts, not ready for distributed |
| Microservices | Large team, independent scaling, domain maturity |
| Event-Driven | Async workflows, decoupling, audit requirements |
| CQRS | Different read/write patterns, high-traffic reads |
| Serverless | Variable load, cost optimization, simple functions |
| Event Sourcing | Audit trail, state reconstruction, complex domain |
