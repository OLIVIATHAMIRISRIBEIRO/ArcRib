# Security Rules

> **Priority**: CRITICAL — Inviolable

---

## Secrets Management

- **NEVER** hardcode secrets in source code
- **ALWAYS** use environment variables via project config
- **BLOCK** commits containing `sk-`, `api_key=`, `password=`, `secret=`
- **MAINTAIN** `.env.example` with all required variables (values redacted)
- `.env` files MUST be in `.gitignore` — no exceptions

---

## Input Validation

- **Backend**: Pydantic/Zod models validate ALL request bodies and query params
- **Frontend**: Zod schemas validate ALL form inputs and API responses
- **NEVER** trust client-side data — re-validate server-side
- **SANITIZE** all input before database writes or AI pipeline consumption
- **LIMIT** payload sizes (request body, file uploads)

---

## Authentication & Authorization

- **JWT** with separate access and refresh token secrets
- **REQUIRE** authentication on all sensitive endpoints
- Rate limiting: **5 login attempts/minute**, **10 API calls/hour/user** (adjust per project)
- **ROTATE** tokens on logout and password change
- Refresh tokens: httpOnly cookies, NOT localStorage

---

## Data Protection

> Projects processing PII must comply with applicable data protection regulations (GDPR, CCPA, etc.).

| Principle          | Implementation                                  |
| :----------------- | :---------------------------------------------- |
| Data minimization  | Collect only what's needed for the feature      |
| Purpose limitation | Document why each data field is collected       |
| Right to erasure   | User account deletion cascades to all user data |
| Data encryption    | PII encrypted at rest (database-level)          |
| Transfer security  | HTTPS enforced for all API communication        |
| Consent            | Explicit opt-in for AI processing of user data  |
| Retention          | Define and enforce data retention periods       |

---

## API Security

- **CORS**: Restrict to known origins only (project domains + localhost)
- **Headers**: Set security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`)
- **Logging**: Log auth failures, never log passwords or tokens
- **Dependencies**: Run `npm audit` and `pip audit` before releases

---

## AI Pipeline Safety

- **NEVER** send raw user PII to external AI providers without anonymization review
- **LOG** all AI API calls for audit trail (sans PII)
- **VALIDATE** AI outputs before presenting to users (hallucination guards)
- **RATE LIMIT** AI provider calls to prevent cost overruns
