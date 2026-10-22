# Domain-Specific Plan Enhancers

> When the loading engine matches specific domains for a task, the planner
> MUST include the corresponding domain-specific sections below.
> These sections are additive to the base plan schema (Tier 1 + Tier 2).

---

## Frontend Domain

**Triggered when**: `frontend` domain matched (keywords: react, next.js, component, css, ui, ux, etc.)

Include in plan:

- **Accessibility (WCAG 2.1 AA)**: Identify components requiring ARIA labels, keyboard navigation, screen reader support, color contrast compliance (minimum 4.5:1 normal text, 3:1 large text)
- **Responsive Design**: Specify breakpoints to test (mobile 375px, tablet 768px, desktop 1280px), identify layout changes per breakpoint, verify touch targets (minimum 44x44px)
- **Bundle Size Impact**: Estimate size of new dependencies, identify tree-shaking opportunities, consider code splitting for new routes, set bundle budget (initial JS < 200KB gzipped)
- **Core Web Vitals**: Assess impact on LCP (< 2.5s), CLS (< 0.1), INP (< 200ms), identify render-blocking resources
- **Component Composition**: Specify component hierarchy, prop interfaces, state management approach (local vs. global), identify shared components for extraction
- **Rendering Strategy**: SSR vs CSR vs ISR decision for each route, hydration impact assessment, streaming SSR opportunities
- **Design System Compliance**: Verify alignment with existing design tokens (colors, spacing, typography), identify new tokens required
- **Error Boundaries**: Define error boundary placement, fallback UI for each failure mode, error reporting integration

---

## Backend Domain

**Triggered when**: `backend` domain matched (keywords: api, server, node, express, middleware, endpoint, etc.)

Include in plan:

- **API Contract**: Define request/response schemas (Zod validation), HTTP methods, status codes, error response format (RFC 7807 Problem Details), versioning strategy
- **Error Handling**: Specify error response structure, error codes, client-facing messages vs. internal logging, error correlation IDs for tracing
- **Rate Limiting**: Identify endpoints requiring rate limits, specify limits (requests/minute/user), throttling strategy (sliding window vs. token bucket), response headers (X-RateLimit-*)
- **Middleware Chain**: Document new middleware additions, execution order, impact on existing middleware stack, short-circuit conditions
- **Database Interaction**: Query patterns (parameterized), transaction boundaries, connection pooling impact, N+1 query prevention
- **Input Validation**: Validation layer placement (controller vs. middleware), sanitization strategy, content-type enforcement, request size limits
- **Idempotency**: Identify non-idempotent operations, implement idempotency keys for critical mutations, retry safety assessment
- **Observability**: Structured logging format (JSON), request tracing headers (X-Request-ID propagation), health check endpoint specification

---

## Database Domain

**Triggered when**: `database` domain matched (keywords: database, sql, migration, schema, query, orm, etc.)

Include in plan:

- **Migration Rollback**: Write both up and down migrations, test rollback procedure before deploying, zero-downtime migration pattern (expand-contract for schema changes)
- **Index Impact Analysis**: Identify queries affected by schema changes, recommend index additions/removals, estimate query performance impact, verify composite index column order matches query patterns
- **Data Integrity**: Define constraints (foreign keys, unique, not null, check), cascade behavior for deletions, domain invariant enforcement at database level
- **Backup Verification**: Verify backup exists before destructive migrations, test restore procedure for critical tables, point-in-time recovery validation
- **Query Performance**: Benchmark key queries before and after changes (EXPLAIN ANALYZE), set acceptable latency thresholds (p50 < 10ms, p99 < 100ms for OLTP), identify sequential scan risks
- **Consistency Model**: Specify required consistency level (strong/eventual), transaction isolation level selection (Read Committed default, Serializable for financial), optimistic vs. pessimistic locking strategy
- **Data Classification**: Identify PII columns requiring encryption at rest, data retention policy compliance, audit trail requirements for sensitive data mutations
- **Connection Management**: Connection pool sizing for workload (pool_size = num_cores * 2 + disk_spindles), statement timeout configuration, idle connection cleanup

---

## DevOps Domain

**Triggered when**: `devops` domain matched (keywords: deploy, ci, cd, docker, kubernetes, pipeline, etc.)

Include in plan:

- **Infrastructure Changes**: Specify IaC modifications (Dockerfile, docker-compose, CI config), environment variable additions, 12-Factor App compliance check
- **Monitoring & Alerting**: Define new metrics to track, alerting thresholds (SLO-derived), dashboard updates, golden signals coverage (latency, traffic, errors, saturation)
- **Progressive Rollout**: Strategy for deployment (canary → staged → full), rollback triggers (error rate > 1%, latency p99 > 2x baseline), automated rollback criteria, health check endpoints
- **Runbook Updates**: Document operational procedures for the new functionality, incident response steps, escalation paths
- **Environment Parity**: Verify changes work across dev, staging, and production environments, configuration drift detection
- **GitOps Compliance**: Infrastructure changes committed to version control, declarative configuration (desired state, not imperative scripts), automated drift reconciliation
- **Container Security**: Base image selection (distroless/alpine preferred), multi-stage build optimization, no secrets in image layers, vulnerability scanning in CI
- **Observability Pipeline**: Log aggregation configuration, trace sampling strategy, metric cardinality assessment, correlation between logs/traces/metrics

---

## Security Domain

**Triggered when**: `security` domain matched (keywords or implicit triggers: auth, login, signup, form, payment, etc.)

Include in plan (in addition to mandatory security considerations):

- **Threat Model (STRIDE)**: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege — assess each for the change with severity rating
- **Authentication Flow Impact**: How the change affects login, session management, token lifecycle, OAuth 2.0 flow selection (Authorization Code + PKCE for SPAs, Client Credentials for M2M)
- **Data Classification**: Identify data sensitivity levels (public, internal, confidential, restricted), storage and transmission requirements per level
- **Compliance Requirements**: GDPR/CCPA implications (data minimization, consent, right to erasure, breach notification within 72 hours)
- **Secret Management**: New secrets required, rotation policy, storage mechanism (environment variables only), zero hardcoded credentials enforcement
- **Zero Trust Assessment**: Authentication at every boundary (never trust, always verify), least privilege access for new endpoints/services, micro-segmentation for new network paths
- **Supply Chain Security**: New dependency audit (license, maintainer, vulnerability scan), lockfile integrity verification, SRI hashes for CDN resources
- **Input Boundary Defense**: All external inputs validated and sanitized, output encoding for context (HTML/URL/JS), parameterized queries only (no string concatenation)

---

## Performance Domain

**Triggered when**: `performance` domain matched (keywords: slow, optimize, speed, bundle, lighthouse, cache, etc.)

Include in plan:

- **Performance Budget**: Define acceptable thresholds (LCP < 2.5s, FID < 100ms, page load < 3s, API p99 < 500ms, memory < 512MB per process)
- **Profiling Strategy**: Tools and methods to measure before/after (Lighthouse, Chrome DevTools, load testing with k6/Artillery), baseline measurement requirements
- **Caching Architecture**: Cache layers (browser → CDN → application → database), TTL values per layer, invalidation strategy (time-based, event-driven, version-key), cache stampede prevention (stale-while-revalidate, locking)
- **Lazy Loading**: Identify resources for deferred loading, intersection observer patterns, dynamic imports for route-level code splitting, image loading strategy (responsive images, next-gen formats)
- **Benchmarking**: Define benchmark suite, baseline measurements, regression detection thresholds, automated performance gates in CI
- **Database Query Optimization**: EXPLAIN ANALYZE for new/modified queries, index coverage verification, N+1 detection, read replica routing for heavy reads
- **Concurrency Model**: Event loop impact assessment, worker thread candidates for CPU-intensive operations, connection pool saturation risk
- **CDN Strategy**: Edge caching rules for static assets, cache-control header specification, origin shield configuration, geographic distribution assessment

---

## Mobile Domain

**Triggered when**: `mobile` domain matched (keywords: mobile, react native, expo, ios, android, etc.)

Include in plan:

- **Platform Parity**: Identify iOS vs. Android differences in behavior, UI, or API access, platform-specific code paths (#ifdef equivalent)
- **Offline Support**: Define offline behavior, data sync strategy (optimistic vs. pessimistic), conflict resolution (last-write-wins, CRDT, manual merge), network-aware queries
- **App Store Guidelines**: Compliance with Apple HIG and Material Design 3, review guideline risks, in-app purchase requirements
- **Native Modules**: Bridge requirements, native module dependencies, build configuration changes (Podfile/build.gradle)
- **Device Testing**: Target device matrix, screen size variations, OS version compatibility (minimum iOS 15 / Android API 26)
- **Navigation Architecture**: Navigation pattern selection (stack, tab, drawer), deep linking support, back navigation handling per platform
- **Mobile Performance Budget**: App startup time < 2s, frame rate 60fps minimum, memory usage < 150MB, APK/IPA size budget
- **State Persistence**: Local storage strategy (AsyncStorage, SQLite, MMKV), state rehydration on app resume, background task handling

---

## Reliability Domain

**Triggered when**: `reliability` domain matched (keywords: reliability, uptime, monitoring, sre, sla, slo, sli, etc.)

Include in plan:

- **SLO Definition**: Define Service Level Objectives for affected services (availability target, latency targets at p50/p95/p99, error rate budget)
- **SLI Instrumentation**: Specify Service Level Indicators to measure (request success rate, request latency, system throughput), measurement method and data source
- **Error Budget Impact**: Assess how the change affects existing error budgets, define acceptable error budget consumption for rollout
- **Golden Signals**: Monitoring for all four golden signals (latency, traffic, errors, saturation) for new/modified services
- **Resilience Patterns**: Circuit breaker placement, retry policy (exponential backoff with jitter), timeout configuration, bulkhead isolation for critical paths
- **Incident Preparedness**: Runbook for new failure modes, alerting rules (page vs. ticket), escalation matrix, blast radius assessment
- **Chaos Engineering**: Identify failure injection points for validation, steady-state hypothesis, abort conditions for chaos experiments
- **Capacity Planning**: Resource requirements (CPU, memory, network, storage), scaling triggers (auto-scale thresholds), load testing validation for expected traffic growth

---

## Observability Domain

**Triggered when**: `observability` domain matched (keywords: logging, tracing, metrics, monitoring, alerting, opentelemetry, etc.)

Include in plan:

- **Three Pillars Coverage**: Specify logging additions (structured JSON), metrics (counters, histograms, gauges), traces (span creation, context propagation)
- **OpenTelemetry Integration**: SDK initialization, auto-instrumentation scope, manual span creation for business-critical paths, sampling strategy (head-based vs. tail-based)
- **Log Architecture**: Log levels and when to use each (ERROR: actionable failures, WARN: degradation, INFO: business events, DEBUG: development only), structured fields, correlation ID propagation
- **Alerting Strategy**: Alert conditions derived from SLOs, notification channels (PagerDuty/Slack), alert fatigue prevention (multi-window burn rate), silence/snooze policies
- **Dashboard Design**: Key metrics visualization, RED method (Rate, Errors, Duration) per service, drill-down capability from overview to detail
- **Cost Management**: Metric cardinality assessment, log volume projection, trace sampling rate optimization, retention policy per signal type

---

## Distributed Systems Domain

**Triggered when**: `architecture` domain matched AND task involves multiple services, message queues, or event-driven patterns

Include in plan:

- **Consistency Strategy**: CAP theorem trade-off for the specific use case, consistency model selection (strong, eventual, causal), Saga pattern for distributed transactions (choreography vs. orchestration)
- **Communication Pattern**: Synchronous (REST/gRPC) vs. asynchronous (message queue/event stream) decision per interaction, protocol selection criteria
- **Fault Tolerance**: Failure mode analysis for each service interaction, fallback behavior, partial failure handling, data loss prevention
- **Event-Driven Design**: Event schema definition (CloudEvents format), event ordering guarantees, idempotent consumers, dead letter queue strategy
- **Service Discovery**: Registration mechanism, health check protocol, load balancing strategy (client-side vs. server-side), circuit breaker integration
- **Data Sovereignty**: Which service owns which data, cross-service data access patterns (API calls, not shared databases), eventual consistency reconciliation

---

## Usage

The planner reads this file when domain-specific sections are needed:

1. Loading engine returns `matchedDomains` array
2. For each matched domain, include the corresponding enhancer section
3. Domain sections are added AFTER the base plan schema sections
4. Multiple domains can be active simultaneously (e.g., frontend + backend for a full-stack feature)
5. Each domain section contributes to the plan quality score (+2 bonus per matched domain section present, -2 penalty per missing)
6. Domain enhancers leverage the specialized knowledge of their corresponding elevated agents (e.g., reliability domain draws from reliability-engineer's SRE Golden Signals framework)
