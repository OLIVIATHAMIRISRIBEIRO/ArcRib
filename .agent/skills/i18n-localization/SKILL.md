---
name: i18n-localization
description: Internationalization and localization patterns for multi-language applications
triggers:
  [
    i18n,
    internationalization,
    localization,
    l10n,
    translation,
    multi-language,
    locale,
    rtl,
  ]
---

# Internationalization & Localization

## Overview

This skill provides patterns and best practices for building multi-language applications with proper internationalization (i18n) and localization (l10n) support.

## Core Principles

1. **Separate content from code**: All user-facing strings must be externalized
2. **Use ICU message format**: Support plurals, gender, and context
3. **Plan for RTL**: Layout should adapt to right-to-left languages
4. **Locale-aware formatting**: Dates, numbers, currencies must respect locale
5. **Fallback strategy**: Always have a default language fallback chain

## Recommended Libraries

### React / Next.js

| Library                     | Use Case                              |
| --------------------------- | ------------------------------------- |
| `next-intl`                 | Next.js App Router (recommended)      |
| `react-intl` / `formatjs`   | React apps with ICU support           |
| `i18next` + `react-i18next` | Feature-rich, plugin ecosystem        |
| `lingui`                    | Compile-time extraction, small bundle |

### React Native / Expo

| Library                     | Use Case                      |
| --------------------------- | ----------------------------- |
| `i18next` + `react-i18next` | Cross-platform (web + native) |
| `expo-localization`         | Device locale detection       |
| `react-native-localize`     | Native locale detection       |

### Backend (Node.js)

| Library         | Use Case                 |
| --------------- | ------------------------ |
| `i18next`       | Server-side translations |
| `messageformat` | ICU message compilation  |
| `globalize`     | CLDR-based formatting    |

## File Structure

```
src/
├── locales/
│   ├── en/
│   │   ├── common.json       # Shared translations
│   │   ├── auth.json          # Auth-related strings
│   │   ├── dashboard.json     # Dashboard strings
│   │   └── errors.json        # Error messages
│   ├── tr/
│   │   ├── common.json
│   │   ├── auth.json
│   │   ├── dashboard.json
│   │   └── errors.json
│   └── de/
│       └── ...
├── i18n/
│   ├── config.ts              # i18n configuration
│   ├── types.ts               # Type-safe key definitions
│   └── middleware.ts          # Locale detection middleware
```

## Translation Key Naming Convention

```json
{
  "namespace.component.element": "Translation",

  "auth.login.title": "Sign In",
  "auth.login.emailLabel": "Email Address",
  "auth.login.passwordLabel": "Password",
  "auth.login.submitButton": "Sign In",
  "auth.login.forgotPassword": "Forgot your password?",

  "errors.validation.required": "{field} is required",
  "errors.validation.minLength": "{field} must be at least {min} characters",
  "errors.network.timeout": "Request timed out. Please try again."
}
```

## Key Patterns

### 1. Type-Safe Translations (TypeScript)

```typescript
// types.ts — Generate from default locale JSON
type TranslationKeys = keyof typeof import('./locales/en/common.json');

// Usage with next-intl
import { useTranslations } from 'next-intl';

function LoginForm() {
  const t = useTranslations('auth.login');
  return <h1>{t('title')}</h1>; // Type-checked!
}
```

### 2. Pluralization (ICU Format)

```json
{
  "notifications.count": "{count, plural, =0 {No notifications} one {# notification} other {# notifications}}"
}
```

### 3. Date/Number Formatting

```typescript
// Always use Intl API or library formatters
const formatted = new Intl.DateTimeFormat(locale, {
  year: "numeric",
  month: "long",
  day: "numeric",
}).format(date);

const price = new Intl.NumberFormat(locale, {
  style: "currency",
  currency: "EUR",
}).format(amount);
```

### 4. RTL Support

```css
/* Use logical properties instead of physical */
.container {
  padding-inline-start: 1rem; /* Not padding-left */
  margin-inline-end: 2rem; /* Not margin-right */
  border-inline-start: 2px solid;
}
```

### 5. Next.js App Router Integration

```typescript
// middleware.ts
import createMiddleware from "next-intl/middleware";

export default createMiddleware({
  locales: ["en", "tr", "de"],
  defaultLocale: "en",
  localeDetection: true,
});

export const config = {
  matcher: ["/((?!api|_next|.*\\..*).*)"],
};
```

## Quality Checklist

- [ ] All user-facing strings externalized (no hardcoded text)
- [ ] Pluralization rules applied for countable items
- [ ] Date/time/number formatting uses locale-aware APIs
- [ ] RTL layout tested (if supporting RTL languages)
- [ ] Fallback language chain configured
- [ ] Translation keys are descriptive and namespaced
- [ ] Missing translation handling defined (fallback vs error)
- [ ] SEO: `<html lang="">` and `hreflang` tags set
- [ ] URL structure supports locale (`/en/about` or subdomain)

## Anti-Patterns to Avoid

❌ Hardcoding strings in components
❌ Using string concatenation for translated sentences
❌ Assuming left-to-right layout
❌ Using physical CSS properties (left/right) instead of logical (start/end)
❌ Formatting dates/numbers without locale context
❌ Storing translations in code instead of separate files

---

> **Source**: Antigravity AI Kit — [antigravity-ai-kit](https://github.com/besync-labs/antigravity-ai-kit)
