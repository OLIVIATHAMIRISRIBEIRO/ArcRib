---
name: ui-ux-pro-max
description: UI/UX design intelligence with anti-AI-slop philosophy. 50+ styles, 21 palettes, 50 font pairings, 20 charts, 9 stacks.
---

# ui-ux-pro-max

Comprehensive design guide for web and mobile applications. Contains 67 styles, 96 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 13 technology stacks. Searchable database with priority-based recommendations.

> **Design Philosophy**: Inspired by [Anthropic's frontend-design skill](https://skills.sh/anthropics/skills/frontend-design). Every interface must have a **bold, intentional aesthetic direction** — never generic, never default. Production-grade code with extraordinary creative vision.

## Prerequisites

Check if Python is installed:

```bash
python3 --version || python --version
```

If Python is not installed, install it based on user's OS:

**macOS:**

```bash
brew install python3
```

**Ubuntu/Debian:**

```bash
sudo apt update && sudo apt install python3
```

**Windows:**

```powershell
winget install Python.Python.3.12
```

---

## When to Apply

Reference these guidelines when:

- Designing new UI components or pages
- Choosing color palettes and typography
- Reviewing code for UX issues
- Building landing pages or dashboards
- Implementing accessibility requirements

## Quick Reference — Rule Categories by Priority

### 1. Accessibility (CRITICAL)

- `color-contrast` — Minimum 4.5:1 ratio for normal text
- `focus-states` — Visible focus rings on interactive elements
- `alt-text` — Descriptive alt text for meaningful images
- `aria-labels` — `aria-label` for icon-only buttons
- `keyboard-nav` — Tab order matches visual order
- `form-labels` — Use `<label>` with `for` attribute

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` — Minimum 44×44px touch targets
- `hover-vs-tap` — Use click/tap for primary interactions
- `loading-buttons` — Disable button during async operations
- `error-feedback` — Clear error messages near the problem
- `cursor-pointer` — Add `cursor-pointer` to clickable elements

### 3. Performance (HIGH)

- `image-optimization` — Use WebP, `srcset`, lazy loading
- `reduced-motion` — Check `prefers-reduced-motion`
- `content-jumping` — Reserve space for async content

### 4. Layout & Responsive (HIGH)

- `viewport-meta` — `width=device-width, initial-scale=1`
- `readable-font-size` — Minimum 16px body text on mobile
- `horizontal-scroll` — Ensure content fits viewport width
- `z-index-management` — Define z-index scale (10, 20, 30, 50)

### 5. Typography & Color (MEDIUM)

- `line-height` — Use 1.5–1.75 for body text
- `line-length` — Limit to 65–75 characters per line
- `font-pairing` — Match heading/body font personalities

### 6. Animation (MEDIUM)

- `duration-timing` — Use 150–300ms for micro-interactions
- `transform-performance` — Use `transform`/`opacity`, not `width`/`height`
- `loading-states` — Skeleton screens or spinners

### 7. Style Selection (MEDIUM)

- `style-match` — Match style to product type
- `consistency` — Use same style across all pages
- `no-emoji-icons` — Use SVG icons, not emojis

### 8. Charts & Data (LOW)

- `chart-type` — Match chart type to data type
- `color-guidance` — Use accessible color palettes
- `data-table` — Provide table alternative for accessibility

---

## How to Use This Skill

When user requests UI/UX work (design, build, create, implement, review, fix, improve), follow this workflow:

### Step 0: Design Thinking — Commit to a Bold Aesthetic Direction (REQUIRED)

Before writing ANY code, answer these questions and commit to a clear creative direction:

1. **Purpose**: What problem does this interface solve? Who uses it?
2. **Aesthetic Tone**: Pick a BOLD direction — don't be timid. Choose from:
   - Brutally minimal · Maximalist chaos · Retro-futuristic · Organic/natural
   - Luxury/refined · Playful/toy-like · Editorial/magazine · Brutalist/raw
   - Art deco/geometric · Soft/pastel · Industrial/utilitarian · Neo-gothic
   - Or invent your own — the key is **intentionality, not intensity**
3. **The Memorable Thing**: What's the ONE element someone will remember? A dramatic animation? An unusual color? A surprising layout? Name it explicitly.
4. **Constraints**: Technical requirements (framework, performance, a11y)

> **CRITICAL**: Bold maximalism and refined minimalism both work. What NEVER works is the safe middle — generic, forgettable, "looks like every other AI-generated site." Execute your chosen direction with precision and conviction.

### Step 1: Analyze User Requirements

Extract key information from user request:

- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, etc.
- **Style keywords**: minimal, playful, professional, elegant, dark mode, etc.
- **Industry**: healthcare, fintech, gaming, education, etc.
- **Stack**: React, Vue, Next.js, or default to `html-tailwind`

### Step 2: Generate Design System (REQUIRED)

**Always start with `--design-system`** to get comprehensive recommendations with reasoning:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This command:

1. Searches 5 domains in parallel (product, style, color, landing, typography)
2. Applies reasoning rules from `ui-reasoning.csv` to select best matches
3. Returns complete design system: pattern, style, colors, typography, effects
4. Includes anti-patterns to avoid

**Example:**

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

To save the design system for hierarchical retrieval across sessions, add `--persist`:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

This creates:

- `design-system/MASTER.md` — Global Source of Truth with all design rules
- `design-system/pages/` — Folder for page-specific overrides

**With page-specific override:**

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

This also creates:

- `design-system/pages/dashboard.md` — Page-specific deviations from Master

**How hierarchical retrieval works:**

1. When building a specific page (e.g., "Checkout"), first check `design-system/pages/checkout.md`
2. If the page file exists, its rules **override** the Master file
3. If not, use `design-system/MASTER.md` exclusively

### Step 3: Supplement with Detailed Searches (as needed)

After getting the design system, use domain searches to get additional details:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**When to use detailed searches:**

| Need                  | Domain       | Example                                 |
| --------------------- | ------------ | --------------------------------------- |
| More style options    | `style`      | `--domain style "glassmorphism dark"`   |
| Chart recommendations | `chart`      | `--domain chart "real-time dashboard"`  |
| UX best practices     | `ux`         | `--domain ux "animation accessibility"` |
| Alternative fonts     | `typography` | `--domain typography "elegant luxury"`  |
| Landing structure     | `landing`    | `--domain landing "hero social-proof"`  |

### Step 4: Stack Guidelines (Default: html-tailwind)

Get implementation-specific best practices. If user doesn't specify a stack, **default to `html-tailwind`**.

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

---

## Search Reference

### Available Domains

| Domain       | Use For                              | Example Keywords                                         |
| ------------ | ------------------------------------ | -------------------------------------------------------- |
| `product`    | Product type recommendations         | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style`      | UI styles, colors, effects           | glassmorphism, minimalism, dark mode, brutalism          |
| `typography` | Font pairings, Google Fonts          | elegant, playful, professional, modern                   |
| `color`      | Color palettes by product type       | saas, ecommerce, healthcare, beauty, fintech, service    |
| `landing`    | Page structure, CTA strategies       | hero, hero-centric, testimonial, pricing, social-proof   |
| `chart`      | Chart types, library recommendations | trend, comparison, timeline, funnel, pie                 |
| `ux`         | Best practices, anti-patterns        | animation, accessibility, z-index, loading               |
| `react`      | React/Next.js performance            | waterfall, bundle, suspense, memo, rerender, cache       |
| `web`        | Web interface guidelines             | aria, focus, keyboard, semantic, virtualize              |
| `prompt`     | AI prompts, CSS keywords             | (style name)                                             |

### Available Stacks

| Stack             | Focus                                                 |
| ----------------- | ----------------------------------------------------- |
| `html-tailwind`   | Tailwind utilities, responsive, a11y (DEFAULT)        |
| `react`           | State, hooks, performance, patterns                   |
| `nextjs`          | SSR, routing, images, API routes                      |
| `vue`             | Composition API, Pinia, Vue Router                    |
| `svelte`          | Runes, stores, SvelteKit                              |
| `swiftui`         | Views, State, Navigation, Animation                   |
| `react-native`    | Components, Navigation, Lists                         |
| `flutter`         | Widgets, State, Layout, Theming                       |
| `shadcn`          | shadcn/ui components, theming, forms, patterns        |
| `jetpack-compose` | Composables, Modifiers, State Hoisting, Recomposition |

---

## Example Workflow

**User request:** "Làm landing page cho dịch vụ chăm sóc da chuyên nghiệp"

### Step 1: Analyze Requirements

- Product type: Beauty/Spa service
- Style keywords: elegant, professional, soft
- Industry: Beauty/Wellness
- Stack: html-tailwind (default)

### Step 2: Generate Design System (REQUIRED)

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service elegant" --design-system -p "Serenity Spa"
```

**Output:** Complete design system with pattern, style, colors, typography, effects, and anti-patterns.

### Step 3: Supplement with Detailed Searches (as needed)

```bash
# Get UX guidelines for animation and accessibility
python3 skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# Get alternative typography options if needed
python3 skills/ui-ux-pro-max/scripts/search.py "elegant luxury serif" --domain typography
```

### Step 4: Stack Guidelines

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "layout responsive form" --stack html-tailwind
```

**Then:** Synthesize design system + detailed searches and implement the design.

---

## Output Formats

The `--design-system` flag supports two output formats:

```bash
# ASCII box (default) - best for terminal display
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown - best for documentation
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## Tips for Better Results

1. **Be specific with keywords** - "healthcare SaaS dashboard" > "app"
2. **Search multiple times** - Different keywords reveal different insights
3. **Combine domains** - Style + Typography + Color = Complete design system
4. **Always check UX** - Search "animation", "z-index", "accessibility" for common issues
5. **Use stack flag** - Get implementation-specific best practices
6. **Iterate** - If first search doesn't match, try different keywords
7. **Never converge** - Each design should feel unique; vary themes, fonts, layouts across projects

---

## Landing Page Strategy

> Inspired by [skill-zero/landing-page-design](https://skills.sh/skill-zero/s/landing-page-design). Conversion-focused design decisions for landing pages.

### Above-the-Fold Formula

Everything visible before scrolling must communicate value in **5 seconds**:

```
┌─────────────────────────────────────────────────┐
│ [Logo]            [Nav]          [CTA Button]   │
│                                                 │
│   Headline (6-12 words)                         │
│   ─────────────────────────                     │
│   Subheadline (15-25 words)    [Hero Image]     │
│                                 showing the     │
│   [Primary CTA Button]         OUTCOME, not     │
│   "Start Free Trial"           the product      │
│                                                 │
│   Social proof: "Trusted by 10,000+ teams"      │
│   [logo] [logo] [logo] [logo] [logo]            │
└─────────────────────────────────────────────────┘
```

### Headlines

**Constraint**: 6–12 words. Say what it **DOES**, not what it **IS**.

| ❌ Bad                                          | Why                      |
| ----------------------------------------------- | ------------------------ |
| "Welcome to Our Platform"                       | Says nothing about value |
| "The World's Most Advanced AI-Powered Solution" | Buzzwords, no specifics  |
| "We Help Businesses Grow"                       | Vague, generic           |
| "Next-Generation Enterprise Software"           | What does it DO?         |

| ✅ Good                                                       | Why                   |
| ------------------------------------------------------------- | --------------------- |
| "Turn customer feedback into product features, automatically" | Specific outcome      |
| "The spreadsheet that thinks like a database"                 | Instant mental model  |
| "Find and fix bugs before your users do"                      | Clear value + urgency |

### Hero Images

**Rule**: Show the **OUTCOME**, not the product.

| ❌ Avoid                      | ✅ Use Instead                            |
| ----------------------------- | ----------------------------------------- |
| Screenshot of your dashboard  | Person looking satisfied at clear results |
| Abstract geometric background | Before/after transformation               |
| Stock photo of a handshake    | The end result of using your product      |

### CTA Buttons

**Formula**: `Action verb` + `value/outcome` + `(optional: reduce risk)`

| ❌ Weak      | ✅ Strong                        |
| ------------ | -------------------------------- |
| "Submit"     | "Start Free Trial"               |
| "Continue"   | "Save API Key"                   |
| "Click Here" | "Get My Career Report — Free"    |
| "Learn More" | "See How It Works in 60 Seconds" |

### Proven Section Order

The high-conversion landing page sequence:

1. **Hero** — Headline + subheadline + CTA + hero image
2. **Social Proof** — Logos, testimonial count, or trust badges
3. **Problem** — Name the pain your audience feels
4. **Solution** — Show how your product solves it
5. **Features/Benefits** — 3–5 key capabilities with outcomes
6. **Testimonials** — Real quotes with names and photos
7. **Pricing** (if applicable) — Clear tiers, highlight recommended
8. **FAQ** — Address top 3–5 objections
9. **Final CTA** — Repeat primary CTA with urgency or bonus
10. **Footer** — Links, legal, trust badges

### Social Proof Types

| Type                   | Best For                   | Example                                |
| ---------------------- | -------------------------- | -------------------------------------- |
| **Logo bar**           | B2B, enterprise trust      | "Trusted by Google, Stripe, Vercel"    |
| **Stats**              | Scale and credibility      | "10,000+ teams" or "2M+ jobs analyzed" |
| **Testimonial quotes** | Emotional connection       | Real photo + name + title + quote      |
| **Case studies**       | Complex/expensive products | "How Company X increased revenue 40%"  |
| **Star ratings**       | Consumer products          | "4.8★ from 2,000+ reviews"             |
| **Media mentions**     | Brand awareness            | "As seen in TechCrunch, Forbes"        |

### OG Image for Sharing

Every landing page needs a `1200×630px` OG image:

- Include product name and tagline
- Use brand colors on a clean gradient or photo background
- Must be readable at thumbnail size (large text, high contrast)
- Set via `<meta property="og:image">` in `<head>`

---

## Common Rules for Professional UI

These are frequently overlooked issues that make UI look unprofessional:

### Anti-AI-Slop Rules (MANDATORY)

These patterns are **BANNED** — they signal generic, AI-generated design:

| Banned Pattern                                | Why It's Bad                        | Do Instead                                              |
| --------------------------------------------- | ----------------------------------- | ------------------------------------------------------- |
| Inter, Roboto, Arial as primary font          | Overused default — zero personality | Choose distinctive display + body pairing               |
| Purple gradients on white backgrounds         | The #1 "AI-generated" cliché        | Commit to a curated, context-specific palette           |
| Predictable card grids with rounded corners   | Cookie-cutter, forgettable          | Use asymmetry, overlap, diagonal flow, or grid-breaking |
| Generic hero with centered h1 + subtext + CTA | Every template ever                 | Create spatial interest — offset, layered, editorial    |
| Same fonts/colors across different projects   | Convergence = laziness              | Each project gets a unique aesthetic identity           |
| Solid white/dark backgrounds everywhere       | Flat, lifeless, no atmosphere       | Add depth: gradient meshes, noise, grain, textures      |

### Typography (Elevated)

- **Display fonts**: Choose something distinctive and characterful — NOT the usual suspects
- **Body fonts**: Pair a refined body font that complements (not matches) the display
- **Hierarchy**: Dominant sizes with sharp contrast; avoid evenly-stepped scales
- Use CSS `@font-face` or Google Fonts for premium choices

### Color & Palette Philosophy

- **Dominant + accent** outperforms timid, evenly-distributed palettes
- Commit to a cohesive aesthetic through CSS custom properties
- One bold color choice > five safe ones

### Motion & Animation

- **High-impact moments first**: One well-orchestrated page load with staggered `animation-delay` reveals creates more delight than scattered micro-interactions
- Prioritize CSS-only solutions; use Motion library (Framer Motion) for React when needed
- Scroll-triggered and hover states should **surprise**, not just confirm
- Match complexity to vision: maximalist designs need elaborate animations; minimal designs need surgical precision

### Backgrounds & Visual Depth

Create **atmosphere** — never default to flat solid colors:

| Technique              | When to Use                              |
| ---------------------- | ---------------------------------------- |
| Gradient meshes        | Luxury, modern SaaS, organic themes      |
| Noise / grain textures | Editorial, brutalist, vintage aesthetics |
| Geometric patterns     | Art deco, tech, mathematical themes      |
| Layered transparencies | Glass morphism, depth-focused layouts    |
| Dramatic shadows       | Bold, dramatic, high-contrast designs    |
| Decorative borders     | Refined, editorial, luxury aesthetics    |

### Spatial Composition

- **Unexpected layouts**: Asymmetry, overlap, diagonal flow, grid-breaking elements
- **Generous negative space** OR **controlled density** — both work, the middle doesn't
- Break the 12-column grid when the design demands it

### Icons & Visual Elements

| Rule                       | Do                                              | Don't                                  |
| -------------------------- | ----------------------------------------------- | -------------------------------------- |
| **No emoji icons**         | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emojis like 🎨 🚀 ⚙️ as UI icons   |
| **Stable hover states**    | Use color/opacity transitions on hover          | Use scale transforms that shift layout |
| **Correct brand logos**    | Research official SVG from Simple Icons         | Guess or use incorrect logo paths      |
| **Consistent icon sizing** | Use fixed viewBox (24x24) with w-6 h-6          | Mix different icon sizes randomly      |

### Interaction & Cursor

| Rule                   | Do                                                    | Don't                                        |
| ---------------------- | ----------------------------------------------------- | -------------------------------------------- |
| **Cursor pointer**     | Add `cursor-pointer` to all clickable/hoverable cards | Leave default cursor on interactive elements |
| **Hover feedback**     | Provide visual feedback (color, shadow, border)       | No indication element is interactive         |
| **Smooth transitions** | Use `transition-colors duration-200`                  | Instant state changes or too slow (>500ms)   |

### Light/Dark Mode Contrast

| Rule                      | Do                                  | Don't                                   |
| ------------------------- | ----------------------------------- | --------------------------------------- |
| **Glass card light mode** | Use `bg-white/80` or higher opacity | Use `bg-white/10` (too transparent)     |
| **Text contrast light**   | Use `#0F172A` (slate-900) for text  | Use `#94A3B8` (slate-400) for body text |
| **Muted text light**      | Use `#475569` (slate-600) minimum   | Use gray-400 or lighter                 |
| **Border visibility**     | Use `border-gray-200` in light mode | Use `border-white/10` (invisible)       |

### Layout & Spacing

| Rule                     | Do                                  | Don't                                  |
| ------------------------ | ----------------------------------- | -------------------------------------- |
| **Floating navbar**      | Add `top-4 left-4 right-4` spacing  | Stick navbar to `top-0 left-0 right-0` |
| **Content padding**      | Account for fixed navbar height     | Let content hide behind fixed elements |
| **Consistent max-width** | Use same `max-w-6xl` or `max-w-7xl` | Mix different container widths         |

---

## Pre-Delivery Checklist

Before delivering UI code, verify these items:

### Creative Intentionality (Step 0 Verification)

- [ ] Aesthetic direction was explicitly chosen and documented
- [ ] The "memorable thing" is identifiable — what will users remember?
- [ ] Design does NOT match any anti-AI-slop banned patterns
- [ ] Fonts are distinctive — NOT Inter, Roboto, Arial, or system defaults
- [ ] Background has depth/atmosphere — NOT a flat solid color
- [ ] Layout has spatial interest — NOT a predictable centered grid

### Visual Quality

- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] Brand logos are correct (verified from Simple Icons)
- [ ] Hover states don't cause layout shift
- [ ] Use theme colors directly (bg-primary) not var() wrapper
- [ ] Color palette is cohesive with dominant + accent strategy

### Interaction

- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation
- [ ] At least one high-impact animation moment (page load, scroll reveal, or hover surprise)

### Light/Dark Mode

- [ ] Light mode text has sufficient contrast (4.5:1 minimum)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes
- [ ] Test both modes before delivery

### Layout

- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility

- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected
