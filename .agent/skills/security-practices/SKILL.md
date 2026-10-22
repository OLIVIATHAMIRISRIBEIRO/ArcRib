---
name: security-practices
description: Application security best practices including Zero Trust principles, OAuth 2.0 / OpenID Connect flows, API security, supply chain security, and vulnerability prevention
triggers: [context, security, auth, vulnerability]
---

# Security Practices Skill

> **Purpose**: Apply security best practices to protect applications

---

## Overview

This skill provides security guidelines following OWASP standards and industry best practices.

---

## Authentication

### Password Security

```typescript
// Use bcrypt with cost factor 12
import bcrypt from "bcrypt";

const SALT_ROUNDS = 12;

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(
  password: string,
  hash: string,
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

### JWT Best Practices

```typescript
// Short-lived access tokens
const accessToken = jwt.sign(payload, SECRET, { expiresIn: "15m" });

// Longer-lived refresh tokens (stored securely)
const refreshToken = jwt.sign({ userId }, REFRESH_SECRET, { expiresIn: "7d" });
```

---

## Input Validation

### Never Trust User Input

```typescript
// SQL Injection vulnerable
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Parameterized query
const user = await prisma.user.findUnique({ where: { id: userId } });
```

### Sanitize Output

```typescript
// XSS vulnerable
element.innerHTML = userInput;

// Escape HTML
import DOMPurify from "dompurify";
element.innerHTML = DOMPurify.sanitize(userInput);
```

---

## OWASP Top 10 Checklist

| Risk                     | Mitigation                           |
| :----------------------- | :----------------------------------- |
| **Injection**            | Parameterized queries, ORMs          |
| **Broken Auth**          | Strong passwords, MFA, rate limiting |
| **Sensitive Data**       | Encryption at rest/transit, HTTPS    |
| **XXE**                  | Disable XML external entities        |
| **Broken Access**        | Verify permissions on every request  |
| **Misconfig**            | Security headers, remove defaults    |
| **XSS**                  | Sanitize output, CSP headers         |
| **Insecure Deserialize** | Validate input types                 |
| **Components**           | Keep dependencies updated            |
| **Logging**              | Log security events, monitor         |

---

## Security Headers

```typescript
// Express/NestJS helmet middleware
app.use(helmet());

// Or manually:
res.setHeader("X-Content-Type-Options", "nosniff");
res.setHeader("X-Frame-Options", "DENY");
res.setHeader("X-XSS-Protection", "1; mode=block");
res.setHeader(
  "Strict-Transport-Security",
  "max-age=31536000; includeSubDomains",
);
res.setHeader("Content-Security-Policy", "default-src 'self'");
```

---

## Secrets Management

```bash
# Never commit secrets
# .env file with API_KEY=sk-1234...

# Use environment variables
export API_KEY=$(vault read secret/api-key)

# Use secret managers
# AWS Secrets Manager, HashiCorp Vault, etc.
```

---

## Zero Trust Principles

Zero Trust assumes no implicit trust for any entity inside or outside the network perimeter. Every access request is fully authenticated, authorized, and encrypted before granting access.

| Principle | Implementation | Verification |
| :--- | :--- | :--- |
| **Never trust, always verify** | Authenticate every request regardless of origin; treat internal traffic the same as external | Audit logs confirm no unauthenticated requests reach protected resources |
| **Least privilege** | Grant minimum permissions required; use role-based and attribute-based access control | Periodic access reviews; automated permission drift detection |
| **Assume breach** | Encrypt data at rest and in transit; segment blast radius; implement intrusion detection | Red team exercises; incident response drills validate containment |
| **Micro-segmentation** | Isolate workloads with network policies; service mesh mTLS between microservices | Verify lateral movement is blocked between segments with penetration testing |
| **Continuous validation** | Re-evaluate trust on every request; session tokens with short TTL; step-up auth for sensitive ops | Monitor for session hijacking; alert on anomalous access patterns |
| **Device trust** | Require managed/compliant devices; verify device posture before granting access | Device compliance checks run at connection time and periodically |

---

## OAuth 2.0 / OpenID Connect Flows

### Flow Selection Matrix

| Client Type | Recommended Flow | Reason |
| :--- | :--- | :--- |
| **Web app (SPA)** | Authorization Code + PKCE | No client secret in browser; PKCE prevents interception |
| **Web app (server)** | Authorization Code | Client secret stored server-side securely |
| **Mobile / Desktop** | Authorization Code + PKCE | Public client; PKCE mandatory |
| **Machine-to-Machine** | Client Credentials | No user interaction; service identity via client secret |
| **Legacy (avoid)** | Implicit | Deprecated; tokens exposed in URL fragment |

### Token Storage Requirements

```typescript
// NEVER store access tokens in localStorage (XSS-accessible)
// NEVER store tokens in sessionStorage for long-lived sessions

// Use httpOnly, Secure, SameSite cookies for refresh tokens
res.cookie("refresh_token", token, {
  httpOnly: true,
  secure: true,
  sameSite: "strict",
  maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  path: "/api/auth/refresh",
});

// Keep access tokens in memory only (JS variable)
// They are short-lived (15 min) and re-obtained via refresh
```

### PKCE Implementation

```typescript
import crypto from "crypto";

// Generate code verifier (43-128 chars, unreserved URI characters)
function generateCodeVerifier(): string {
  return crypto.randomBytes(32).toString("base64url");
}

// Derive code challenge from verifier
function generateCodeChallenge(verifier: string): string {
  return crypto.createHash("sha256").update(verifier).digest("base64url");
}

// All public clients MUST use PKCE (RFC 7636)
// Send code_challenge with authorization request
// Send code_verifier with token exchange request
```

---

## API Security

### Rate Limiting Patterns

| Strategy | Use Case | Example |
| :--- | :--- | :--- |
| **Per-endpoint** | Protect expensive operations | `/api/search`: 10 req/min |
| **Per-user** | Fair usage enforcement | Authenticated: 1000 req/hr |
| **Sliding window** | Smooth traffic spikes | Rolling 60s window, max 100 |
| **Token bucket** | Burst tolerance | 10 tokens, refill 1/sec |
| **IP-based** | Unauthenticated endpoints | Login: 5 attempts/15 min |

```typescript
import rateLimit from "express-rate-limit";

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.user?.id ?? req.ip,
});

app.use("/api/", apiLimiter);
```

### API Key Management

- **Rotate keys** on a regular schedule (90 days max) and immediately on suspected compromise
- **Scope keys** to specific endpoints, methods, and IP ranges
- **Never embed keys** in client-side code or version control
- **Use separate keys** for each environment (dev, staging, production)
- **Log key usage** to detect anomalous patterns

### Request Signing

```typescript
// Sign requests with HMAC to prevent tampering
import crypto from "crypto";

function signRequest(payload: string, secret: string): string {
  return crypto.createHmac("sha256", secret).update(payload).digest("hex");
}

// Verify on server side; reject requests with invalid or expired signatures
// Include timestamp in signed payload to prevent replay attacks
```

### API Versioning Security

- Deprecate and remove old API versions that lack current security controls
- Apply the same authentication and authorization to all active versions
- Monitor traffic to deprecated versions for potential abuse
- Never maintain insecure legacy endpoints for backward compatibility

---

## Supply Chain Security

### Dependency Auditing

```bash
# Run audit on every CI build
npm audit --audit-level=high

# Fix known vulnerabilities
npm audit fix

# Use lockfile-only installs in CI to prevent supply chain attacks
npm ci
```

### Lockfile Integrity

- **Always commit** `package-lock.json` to version control
- **Use `npm ci`** in CI/CD pipelines (installs from lockfile exactly)
- **Review lockfile diffs** in pull requests for unexpected changes
- **Enable lockfile-lint** to enforce registry and integrity hash policies

### Dependency Pinning

```json
{
  "dependencies": {
    "express": "4.18.2",
    "prisma": "5.10.0"
  }
}
```

- Pin exact versions in production applications (no `^` or `~`)
- Use Dependabot or Renovate for controlled, reviewed updates
- Separate security patches from feature updates in dependency PRs

### Typosquatting Detection

| Technique | Example |
| :--- | :--- |
| **Character swap** | `expresss` instead of `express` |
| **Hyphen confusion** | `lodash-utils` mimicking `lodash` |
| **Scope squatting** | `@myorg/config` vs `@my-org/config` |

- Verify package publisher and download counts before installing
- Use `npm config set ignore-scripts true` for initial installs, then review scripts
- Consider using Socket.dev or Snyk to detect malicious packages automatically

---

## Quick Reference

| Practice     | Implementation        |
| :----------- | :-------------------- |
| Passwords    | bcrypt, Argon2        |
| Tokens       | Short-lived JWT       |
| SQL          | Parameterized queries |
| XSS          | Sanitize, CSP         |
| HTTPS        | TLS 1.3, HSTS         |
| Secrets      | Environment, vaults   |
| Dependencies | npm audit, Snyk       |
| Logging      | Audit trail, no PII   |
| Zero Trust   | Verify every request  |
| OAuth 2.0    | Auth Code + PKCE      |
| API Keys     | Scoped, rotated       |
| Supply Chain | Lockfile, pin deps    |
