---
name: database-design
description: Database schema design, optimization patterns, distributed system consistency models, and zero-downtime migration strategies
triggers: [context, database, schema, sql, prisma]
---

# Database Design Skill

> **Purpose**: Design efficient, normalized database schemas

---

## Overview

This skill provides guidance for designing performant, scalable database schemas following best practices.

---

## Schema Design Principles

### 1. Normalization (3NF)

- **1NF**: Atomic values, no repeating groups
- **2NF**: No partial dependencies
- **3NF**: No transitive dependencies

### 2. Naming Conventions

```sql
-- Tables: plural, snake_case
users, order_items, user_preferences

-- Columns: singular, snake_case
user_id, created_at, is_active

-- Primary Keys: id or {table}_id
id, user_id

-- Foreign Keys: {referenced_table}_id
user_id, order_id
```

---

## Common Patterns

### User Entity

```prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  firstName String?
  lastName  String?
  role      Role     @default(USER)
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

enum Role {
  USER
  ADMIN
}
```

### One-to-Many

```prisma
model User {
  id     String  @id @default(uuid())
  orders Order[]
}

model Order {
  id     String @id @default(uuid())
  userId String
  user   User   @relation(fields: [userId], references: [id])
}
```

### Many-to-Many

```prisma
model User {
  id    String @id @default(uuid())
  roles Role[]
}

model Role {
  id    String @id @default(uuid())
  users User[]
}
```

---

## Indexing Strategy

```prisma
model User {
  id    String @id @default(uuid())
  email String @unique

  @@index([createdAt])
  @@index([isActive, role])
}
```

### When to Index

| Scenario          | Index Type     |
| :---------------- | :------------- |
| Primary lookup    | Primary Key    |
| Unique constraint | Unique         |
| Frequent WHERE    | B-tree         |
| Text search       | Full-text      |
| JSON fields       | GIN (Postgres) |

---

## Query Optimization

```typescript
// N+1 Problem
const users = await prisma.user.findMany();
for (const user of users) {
  const orders = await prisma.order.findMany({ where: { userId: user.id } });
}

// Eager Loading
const users = await prisma.user.findMany({
  include: { orders: true },
});
```

---

## CAP Theorem

In a distributed system, you can guarantee at most two of three properties simultaneously:

- **Consistency (C)**: Every read returns the most recent write
- **Availability (A)**: Every request receives a response (no timeout)
- **Partition Tolerance (P)**: The system continues operating despite network partitions

Since network partitions are unavoidable in distributed systems, the real choice is between CP and AP.

### Decision Matrix

| Trade-off | Guarantees | Sacrifices | When to Choose | Example Systems |
| :--- | :--- | :--- | :--- | :--- |
| **CP** | Consistency + Partition Tolerance | Availability during partitions | Financial transactions, inventory counts, leader election | MongoDB (default), HBase, Zookeeper |
| **AP** | Availability + Partition Tolerance | Consistency (eventual) | Social feeds, caching layers, DNS, session stores | Cassandra, DynamoDB, CouchDB |
| **CA** | Consistency + Availability | Partition Tolerance | Single-node deployments only (no true distribution) | Traditional RDBMS (PostgreSQL, MySQL single-node) |

---

## ACID vs BASE

### Property Comparison

| Property | ACID | BASE |
| :--- | :--- | :--- |
| **Full name** | Atomicity, Consistency, Isolation, Durability | Basically Available, Soft state, Eventually consistent |
| **Consistency** | Strong (immediate) | Eventual |
| **Availability** | May block under contention | Prioritizes availability |
| **Transactions** | Full multi-statement transactions | Single-record atomic ops; app-level sagas |
| **Scaling** | Vertical first; horizontal is complex | Horizontal by design |
| **Best for** | Financial systems, booking, inventory | Analytics, social, IoT, content delivery |

### When to Use Each

- **ACID**: Money movement, order processing, anything requiring rollback guarantees, regulatory compliance
- **BASE**: High-throughput writes, geographically distributed reads, systems where stale reads are acceptable for seconds

---

## Consistency Models

From strongest to weakest, choose the level your application actually needs:

| Model | Guarantee | Latency Cost | Use Case |
| :--- | :--- | :--- | :--- |
| **Strict / Linearizable** | Reads always see the latest write globally | Highest (cross-region coordination) | Distributed locks, leader election |
| **Sequential** | All nodes see operations in the same order | High | Replicated state machines |
| **Causal** | Causally related operations are seen in order | Medium | Chat applications, collaborative editing |
| **Read-your-writes** | A client always sees its own writes | Low-Medium | User profile updates, shopping carts |
| **Monotonic reads** | Once a value is seen, older values are never returned | Low | Dashboard displays, reporting |
| **Eventual** | All replicas converge given enough time | Lowest | DNS, CDN caches, social media likes |

Choose the weakest model your application can tolerate to maximize performance and availability.

---

## Migration Safety

### Zero-Downtime Migration Pattern

Safe migrations follow a multi-phase approach that avoids locking tables or breaking running application code.

**Phase 1 - Expand**: Add new structures alongside old ones
**Phase 2 - Migrate**: Backfill data, dual-write to both structures
**Phase 3 - Contract**: Remove old structures after all consumers have switched

### Safe vs Unsafe Operations

| Operation | Safe? | Zero-Downtime Alternative |
| :--- | :--- | :--- |
| **Add nullable column** | Safe | N/A (already safe) |
| **Add column with default** | Safe (Postgres 11+) | For older versions, add nullable then backfill |
| **Drop column** | Unsafe | Stop reading column in code first, then drop in next deploy |
| **Rename column** | Unsafe | Add new column, dual-write, migrate reads, drop old |
| **Change column type** | Unsafe | Add new column with new type, backfill, swap reads |
| **Add NOT NULL constraint** | Unsafe | Add CHECK constraint as NOT VALID, then VALIDATE separately |
| **Add index** | Unsafe (locks table) | Use `CREATE INDEX CONCURRENTLY` (Postgres) |
| **Drop table** | Unsafe | Remove all references in code first, then drop |

### Backfill Pattern

```typescript
// Backfill in batches to avoid long-running transactions
async function backfillNewColumn(batchSize = 1000) {
  let processed = 0;
  let hasMore = true;

  while (hasMore) {
    const rows = await prisma.$executeRaw`
      UPDATE users
      SET display_name = first_name || ' ' || last_name
      WHERE display_name IS NULL
      LIMIT ${batchSize}
    `;

    processed += rows;
    hasMore = rows === batchSize;

    // Yield to other operations between batches
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  return processed;
}
```

---

## Connection Pooling

### Pool Size Guidance

| Environment | Pool Size | Rationale |
| :--- | :--- | :--- |
| **Development** | 2-5 | Single developer, minimal concurrency |
| **Production (server)** | 10-20 per instance | Balance between concurrency and DB connection limits |
| **Production (serverless)** | 1-2 per function | Functions scale horizontally; too many connections exhaust DB limits |
| **Staging / CI** | 3-5 | Mirrors production behavior without resource waste |

### Sizing Formula

```
max_pool_size = (db_max_connections - reserved_superuser_connections) / number_of_app_instances
```

For PostgreSQL with `max_connections = 100`, 3 superuser slots reserved, and 4 app instances:
`(100 - 3) / 4 = ~24 connections per instance`

### Tool Recommendations

| Tool | Best For | Notes |
| :--- | :--- | :--- |
| **PgBouncer** | External pooler for PostgreSQL | Transaction-mode pooling for serverless; sits between app and DB |
| **Prisma built-in pool** | Prisma ORM users | Configure via `connection_limit` in datasource URL |
| **Prisma Accelerate** | Serverless / edge | Managed connection pooling with global caching |
| **RDS Proxy** | AWS deployments | Managed pooler; supports IAM auth and failover |
| **Supabase Supavisor** | Supabase projects | Built-in pooler with transaction and session modes |

```prisma
// Prisma connection pool configuration
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL") // ?connection_limit=20&pool_timeout=10
}
```

---

## Quick Reference

| Pattern        | Usage               |
| :------------- | :------------------ |
| UUID           | Distributed systems |
| Auto-increment | Simple apps         |
| Soft Delete    | Audit requirements  |
| Timestamps     | Always include      |
| Indexes        | Frequent queries    |
| Constraints    | Data integrity      |
| CAP trade-off  | Distributed design  |
| ACID           | Transactional data  |
| BASE           | High-scale writes   |
| Migrations     | Zero-downtime deploys |
| Connection Pool | Right-size per env |
