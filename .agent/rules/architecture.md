# Architecture Rules

> **Priority**: HIGH — Enforced in design reviews
> **Scope**: All workspaces — universal architectural constraints

---

## Architecture Principles

| Principle                | Enforcement                                                   |
| :----------------------- | :------------------------------------------------------------ |
| Separation of Concerns   | Each module has a single, well-defined responsibility         |
| Dependency Direction     | Dependencies ALWAYS point inward — domain never imports infra |
| Contract-First Design    | Define API contracts before implementation begins             |
| Explicit Over Implicit   | Configuration, dependencies, and boundaries must be explicit  |
| Composition Over Inherit | Prefer composition and dependency injection over inheritance  |

---

## Boundary Enforcement

- **NEVER** import backend code from frontend or vice versa
- **NEVER** skip architectural layers — each layer imports only from the layer directly below
- **NEVER** hold direct object references across aggregate or module boundaries — use IDs
- Shared types and contracts are defined at the API boundary and replicated per consumer
- Cross-module communication uses events or explicit service interfaces, not direct coupling

---

## Project Structure

Projects should follow one of these organizational patterns:

| Pattern          | When to Use                                              |
| :--------------- | :------------------------------------------------------- |
| **Monorepo**     | Multiple apps sharing code (Turborepo, Nx, Rush)         |
| **Polyrepo**     | Independent services with separate lifecycles            |
| **Modular Mono** | Single deployable with clear bounded context separation  |

> **Customization**: Project-specific structure decisions should be documented in `decisions/` as Architecture Decision Records (ADRs).

---

## Layered Architecture

```
Thin Routes / Controllers → Service Layer → Models / Data Access
                              ↕
                          Domain Logic
```

| Layer            | Responsibility                            | Rules                                              |
| :--------------- | :---------------------------------------- | :------------------------------------------------- |
| Routes           | HTTP handling, auth enforcement           | MAX 10 lines per handler, delegate to services      |
| Services         | Business logic, validation, orchestration | Pure functions where possible, fully testable       |
| Models / Data    | Database schema, relationships            | ORM-managed, migration-controlled                   |
| Schemas          | Request/response contracts                | Validated models, explicit field constraints         |

---

## Database Conventions

- **Migrations** for ALL schema changes — no manual SQL in production
- Table names: `snake_case`, plural (`users`, `funnel_events`)
- Column names: `snake_case`
- Always include: `id` (UUID recommended), `created_at`, `updated_at`
- Foreign keys: `<entity>_id` naming convention
- Indexes: create for all foreign keys and frequent query columns
- Soft deletes preferred over hard deletes for audit-sensitive data

---

## API Design Principles

| Principle            | Standard                                                    |
| :------------------- | :---------------------------------------------------------- |
| Versioning           | URL-prefix (`/api/v1/`) or header-based — be consistent    |
| Methods              | Standard HTTP methods and status codes (RESTful)            |
| Response Format      | All endpoints return validated, structured JSON             |
| Pagination           | Offset-based (`skip`/`limit`) or cursor-based — documented |
| Error Format         | `{ "detail": "Human-readable message" }` minimum           |
| Rate Limiting        | Documented per endpoint, enforced server-side               |

---

## Architecture Decision Records

When making significant architectural decisions, document them using ADRs in the `decisions/` directory:

- Choosing between architectural approaches (monolith vs microservices)
- Selecting a technology (database, framework, library)
- Establishing a pattern (event sourcing vs CRUD)
- Making a trade-off (consistency vs availability)

ADR format: `decisions/adr-NNN-<decision-title>.md`

---

## Related Resources

- **Skill**: `.agent/skills/architecture/SKILL.md` — deep architectural patterns (DDD, Clean Architecture, 12-Factor, SOLID)
- **Agent**: `.agent/agents/architect.md` — architecture review process and checklists

---

## Version History

| Version | Date       | Changes                                                |
| :------ | :--------- | :----------------------------------------------------- |
| 1.0.0   | 2026-03-16 | Initial generic architecture enforcement rules for kit |

