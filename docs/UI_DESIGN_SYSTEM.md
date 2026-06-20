# A2Z Tools — UI Design System

**Australian Hardware & Networking Ecommerce Platform**

| Attribute | Value |
|-----------|-------|
| **Product** | A2Z Tools |
| **Version** | 1.0 |
| **Market** | Australia |
| **Audience** | Trade Professionals, Electricians, Network Installers, Contractors, Businesses, DIY |
| **Approach** | Mobile-first, enterprise-grade, WCAG 2.1 AA |
| **Stack** | Next.js 15 · TailwindCSS · ShadCN UI |

---

## Table of Contents

1. [Brand Identity](#1-brand-identity)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [Grid System](#4-grid-system)
5. [Spacing System](#5-spacing-system)
6. [Buttons](#6-buttons)
7. [Forms](#7-forms)
8. [Product Cards](#8-product-cards)
9. [Product Detail Pages](#9-product-detail-pages)
10. [Navigation](#10-navigation)
11. [Footer](#11-footer)
12. [Mobile Design Rules](#12-mobile-design-rules)
13. [Desktop Design Rules](#13-desktop-design-rules)
14. [Dashboard Design System](#14-dashboard-design-system)
15. [Icon System](#15-icon-system)
16. [Animation Guidelines](#16-animation-guidelines)
17. [Accessibility Standards](#17-accessibility-standards)

---

## 1. Brand Identity

### 1.1 Brand Positioning

A2Z Tools occupies the intersection of **enterprise networking authority** (Cisco, Ubiquiti) and **trade-grade reliability** (Bunnings Trade, RS Components), with the **procurement efficiency** of Amazon Business. The visual language must communicate:

| Attribute | Expression |
|-----------|------------|
| **Professional** | Restrained colour use, structured layouts, no decorative clutter |
| **Premium** | Generous whitespace, refined typography, high-quality product photography |
| **Modern** | Clean lines, subtle depth, contemporary component patterns |
| **Trustworthy** | Clear pricing, visible stock status, Australian business credentials |
| **Efficient** | Fast paths to purchase, scannable specs, minimal friction checkout |

### 1.2 Brand Personality

```
Authoritative ────────●──────── Approachable
(Technical expert)              (Trade-friendly)

Corporate ────────────●──────── Practical
(Enterprise-grade)              (Job-site ready)

Premium ──────────────●──────── Accessible
(Quality focus)                 (Fair pricing, DIY welcome)
```

### 1.3 Logo Usage

| Variant | Use Case |
|---------|----------|
| **Primary logo** | Header, marketing, invoices — full colour on light backgrounds |
| **Reversed logo** | Dark headers, hero overlays, footer on dark background |
| **Logomark** | Favicon, app icon, compact mobile header, social avatars |
| **Monochrome** | Watermarks, single-colour print, embossing |

**Clear space:** Minimum padding equal to the height of the "A" in the logotype on all sides.

**Minimum sizes:**
- Digital full logo: 120px width minimum
- Logomark only: 32px × 32px minimum
- Print: 25mm width minimum

**Do not:** Stretch, rotate, apply gradients to the logo, place on busy photography without a scrim, or use unapproved colour variants.

### 1.4 Voice & Tone (UI Copy)

| Context | Tone | Example |
|---------|------|---------|
| Product descriptions | Technical, precise | "24-port Gigabit PoE+ switch, 370W budget, fanless design" |
| CTAs | Direct, action-oriented | "Add to Cart", "Request Trade Quote", "Check Stock" |
| Errors | Helpful, non-blaming | "This postcode isn't in our delivery area. Try click & collect." |
| Trade account | Professional, respectful | "Your trade pricing is applied", "Net 30 terms available" |
| DIY | Friendly, guiding | "Not sure which cable? See our buying guide." |

### 1.5 Photography & Imagery

| Type | Guidelines |
|------|-------------|
| **Product shots** | White or light grey (#F8FAFC) background, consistent shadow, multiple angles |
| **Lifestyle** | Real Australian job sites — commercial buildings, ceiling installs, rack rooms |
| **People** | Diverse tradespeople in PPE; authentic, not stock-photo sterile |
| **Technical diagrams** | Clean line drawings for installation guides; brand accent colour for highlights |
| **Brand logos** | Official manufacturer logos at consistent height in brand grids |

**Avoid:** Clip art, excessive lens flare, US-centric settings, cluttered workshop imagery.

### 1.6 Design Principles

1. **Clarity over cleverness** — Users are on job sites; every element must be instantly understood
2. **Specs are first-class** — Technical data is never hidden behind unnecessary interaction
3. **Price transparency** — AUD, GST status, and trade pricing always visible where applicable
4. **Thumb-zone priority** — Primary actions live within comfortable one-handed reach on mobile
5. **Progressive disclosure** — Show essentials first; detail on demand
6. **Consistent density** — Trade users want information density; DIY users get simplified defaults

---

## 2. Color Palette

### 2.1 Core Brand Colors

Inspired by enterprise networking (Cisco blue depth, Ubiquiti precision) with Australian trade visibility.

| Token | Name | Hex | RGB | Usage |
|-------|------|-----|-----|-------|
| `--brand-primary` | A2Z Navy | `#0F172A` | 15, 23, 42 | Headers, primary text, dark surfaces |
| `--brand-primary-light` | Slate 800 | `#1E293B` | 30, 41, 59 | Secondary dark surfaces, hover states |
| `--brand-accent` | Network Blue | `#0066CC` | 0, 102, 204 | Primary CTAs, links, focus rings, active nav |
| `--brand-accent-hover` | Blue 700 | `#0052A3` | 0, 82, 163 | Button hover, link hover |
| `--brand-accent-light` | Blue 50 | `#EFF6FF` | 239, 246, 255 | Selected states, info backgrounds |
| `--brand-secondary` | Trade Amber | `#D97706` | 217, 119, 6 | Trade badges, promotions, urgency accents |
| `--brand-secondary-light` | Amber 50 | `#FFFBEB` | 255, 251, 235 | Promo banners, sale backgrounds |

### 2.2 Neutral Palette

Cool neutrals convey technical precision and pair well with product photography.

| Token | Name | Hex | Usage |
|-------|------|-----|-------|
| `--neutral-0` | White | `#FFFFFF` | Page backgrounds, cards |
| `--neutral-50` | Slate 50 | `#F8FAFC` | Alternate backgrounds, input fields |
| `--neutral-100` | Slate 100 | `#F1F5F9` | Dividers, disabled backgrounds |
| `--neutral-200` | Slate 200 | `#E2E8F0` | Borders, separators |
| `--neutral-300` | Slate 300 | `#CBD5E1` | Placeholder borders, inactive icons |
| `--neutral-400` | Slate 400 | `#94A3B8` | Placeholder text, meta labels |
| `--neutral-500` | Slate 500 | `#64748B` | Secondary text, captions |
| `--neutral-600` | Slate 600 | `#475569` | Body text (light backgrounds) |
| `--neutral-700` | Slate 700 | `#334155` | Emphasised body text |
| `--neutral-800` | Slate 800 | `#1E293B` | Headings on light bg |
| `--neutral-900` | Slate 900 | `#0F172A` | Primary headings |

### 2.3 Semantic Colors

| Token | Name | Hex | Usage |
|-------|------|-----|-------|
| `--success` | Stock Green | `#059669` | In stock, order confirmed, success states |
| `--success-light` | Emerald 50 | `#ECFDF5` | Success alert backgrounds |
| `--warning` | Caution Amber | `#D97706` | Low stock, backorder, pending |
| `--warning-light` | Amber 50 | `#FFFBEB` | Warning alert backgrounds |
| `--error` | Alert Red | `#DC2626` | Out of stock, errors, destructive actions |
| `--error-light` | Red 50 | `#FEF2F2` | Error alert backgrounds |
| `--info` | Info Blue | `#0066CC` | Informational notices, tips |
| `--info-light` | Blue 50 | `#EFF6FF` | Info alert backgrounds |

### 2.4 Surface & Elevation

| Token | Value | Usage |
|-------|-------|-------|
| `--surface-page` | `#FFFFFF` | Main page background |
| `--surface-subtle` | `#F8FAFC` | Alternating sections, filter panels |
| `--surface-raised` | `#FFFFFF` + shadow-sm | Cards, dropdowns |
| `--surface-overlay` | `#FFFFFF` + shadow-lg | Modals, popovers |
| `--surface-dark` | `#0F172A` | Footer, dark hero sections |
| `--surface-dark-elevated` | `#1E293B` | Dark cards, mobile nav drawer |

**Shadow tokens:**

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-xs` | 0 1px 2px rgba(15,23,42,0.05) | Subtle lift |
| `--shadow-sm` | 0 1px 3px rgba(15,23,42,0.08), 0 1px 2px rgba(15,23,42,0.04) | Cards |
| `--shadow-md` | 0 4px 6px rgba(15,23,42,0.06), 0 2px 4px rgba(15,23,42,0.04) | Dropdowns, hover cards |
| `--shadow-lg` | 0 10px 15px rgba(15,23,42,0.08), 0 4px 6px rgba(15,23,42,0.04) | Modals, mobile drawers |
| `--shadow-focus` | 0 0 0 3px rgba(0,102,204,0.35) | Focus ring |

### 2.5 Color Usage Rules

| Rule | Guideline |
|------|-----------|
| **60-30-10** | 60% neutrals, 30% navy/dark, 10% accent blue |
| **CTA hierarchy** | One primary blue CTA per viewport section |
| **Trade amber** | Reserved for trade-specific UI — never for primary checkout |
| **GST display** | Price text in `--neutral-900`; GST label in `--neutral-500` |
| **Dark mode** | Phase 2 — tokens reserved; not in MVP |
| **Contrast** | All text/background pairs must meet WCAG AA (4.5:1 body, 3:1 large text) |

### 2.6 Color Accessibility Matrix

| Combination | Ratio | Pass |
|-------------|-------|------|
| Navy `#0F172A` on White | 17.9:1 | AAA |
| Slate 600 `#475569` on White | 6.1:1 | AA |
| Network Blue `#0066CC` on White | 5.6:1 | AA |
| White on Network Blue `#0066CC` | 5.6:1 | AA |
| White on Navy `#0F172A` | 17.9:1 | AAA |
| Trade Amber `#D97706` on White | 3.4:1 | AA Large text only |
| Success Green `#059669` on White | 4.5:1 | AA |

---

## 3. Typography

### 3.1 Font Stack

| Role | Family | Fallback | Rationale |
|------|--------|----------|-----------|
| **Primary** | Inter | system-ui, sans-serif | Enterprise clarity, excellent legibility at small sizes |
| **Monospace** | JetBrains Mono | ui-monospace, monospace | SKUs, part numbers, IP addresses, order IDs |

**Loading:** `font-display: swap` for Inter; subset to Latin character set.

### 3.2 Type Scale

Based on a **1.250 (Major Third)** scale with 16px root.

| Token | Size | Line Height | Weight | Letter Spacing | Usage |
|-------|------|-------------|--------|----------------|-------|
| `text-xs` | 12px / 0.75rem | 16px | 400–500 | 0.01em | Legal, fine print, badges |
| `text-sm` | 14px / 0.875rem | 20px | 400–500 | 0 | Meta, captions, table cells |
| `text-base` | 16px / 1rem | 24px | 400 | 0 | Body copy, form inputs |
| `text-lg` | 18px / 1.125rem | 28px | 400–500 | 0 | Lead paragraphs, card descriptions |
| `text-xl` | 20px / 1.25rem | 28px | 500–600 | -0.01em | Card titles, section labels |
| `text-2xl` | 24px / 1.5rem | 32px | 600 | -0.01em | Page subheadings |
| `text-3xl` | 30px / 1.875rem | 36px | 600–700 | -0.02em | Page titles (mobile) |
| `text-4xl` | 36px / 2.25rem | 40px | 700 | -0.02em | Page titles (desktop) |
| `text-5xl` | 48px / 3rem | 48px | 700 | -0.02em | Hero headlines (desktop only) |

### 3.3 Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text, descriptions |
| Medium | 500 | Labels, nav items, buttons |
| Semibold | 600 | Subheadings, card titles, prices |
| Bold | 700 | Page titles, hero text, emphasis |

**Avoid:** Weight 300 (too light for job-site screen visibility) and weight 800+ (too heavy for dense catalog pages).

### 3.4 Typographic Patterns

| Pattern | Specification |
|---------|---------------|
| **Product title** | `text-lg` semibold, `--neutral-900`, max 2 lines with ellipsis |
| **SKU / Part number** | `text-sm` monospace, `--neutral-500` |
| **Price (retail)** | `text-xl` semibold, `--neutral-900` |
| **Price (trade)** | `text-xl` semibold, `--brand-accent` + "Trade" badge |
| **Price (was/RRP)** | `text-sm` regular, `--neutral-400`, strikethrough |
| **GST suffix** | `text-xs` regular, `--neutral-500` — "inc. GST" or "ex. GST" |
| **Spec label** | `text-sm` medium, `--neutral-600` |
| **Spec value** | `text-sm` regular, `--neutral-900` |
| **Section heading** | `text-2xl` semibold, `--neutral-900`, 24px margin below |
| **Breadcrumb** | `text-sm` regular, `--neutral-500`, current page `--neutral-900` |

### 3.5 Responsive Typography

| Breakpoint | Body | H1 | H2 | Product Title |
|------------|------|----|----|---------------|
| Mobile (<640px) | 16px | 30px | 24px | 16px |
| Tablet (640–1024px) | 16px | 36px | 24px | 18px |
| Desktop (>1024px) | 16px | 36–48px | 30px | 18px |

---

## 4. Grid System

### 4.1 Breakpoints

| Token | Min Width | Target Devices |
|-------|-----------|----------------|
| `xs` | 0px | Small phones (320px+) |
| `sm` | 640px | Large phones, small tablets |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops, landscape tablets |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large monitors |

**Design approach:** Mobile-first — base styles target 320–639px; breakpoints add complexity upward.

### 4.2 Container Widths

| Breakpoint | Max Width | Horizontal Padding |
|------------|-----------|-------------------|
| xs–sm | 100% | 16px |
| md | 100% | 24px |
| lg | 1024px | 32px |
| xl | 1280px | 32px |
| 2xl | 1440px | 32px |

**Content max-width:** 1440px — prevents excessive line length on ultrawide displays.

### 4.3 Column Grid

| Breakpoint | Columns | Gutter | Margin |
|------------|---------|--------|--------|
| Mobile | 4 | 16px | 16px |
| Tablet | 8 | 24px | 24px |
| Desktop | 12 | 24px | 32px |
| Wide | 12 | 32px | auto (centred) |

### 4.4 Layout Regions

```
┌────────────────────────────────────────────────────────────┐
│  ANNOUNCEMENT BAR (optional, 40px)                          │
├────────────────────────────────────────────────────────────┤
│  HEADER (64px mobile / 72px desktop)                        │
├────────────────────────────────────────────────────────────┤
│  BREADCRUMB (40px, desktop + PDP/category only)             │
├──────────┬─────────────────────────────────────────────────┤
│          │                                                  │
│  SIDEBAR │  MAIN CONTENT                                    │
│  (filters│  (product grid, PDP, checkout)                   │
│  280px)  │                                                  │
│          │                                                  │
│  desktop │                                                  │
│  only    │                                                  │
├──────────┴─────────────────────────────────────────────────┤
│  FOOTER                                                     │
└────────────────────────────────────────────────────────────┘
```

### 4.5 Common Layout Patterns

| Pattern | Mobile | Desktop |
|---------|--------|---------|
| Product listing grid | 2 columns | 3–4 columns |
| Product detail | Single column stack | 2 columns (gallery 55% / info 45%) |
| Cart | Full-width stacked items | 65% items / 35% summary sidebar |
| Checkout | Single column stepper | 60% form / 40% order summary |
| Account dashboard | Single column cards | 240px sidebar nav + content area |
| Spec comparison table | Horizontal scroll | Full-width table |

---

## 5. Spacing System

### 5.1 Base Unit

**4px base unit** — all spacing values are multiples of 4.

| Token | Value | Usage |
|-------|-------|-------|
| `space-0` | 0px | Reset |
| `space-0.5` | 2px | Tight icon gaps |
| `space-1` | 4px | Inline icon padding |
| `space-2` | 8px | Compact element gaps |
| `space-3` | 12px | Form field internal padding |
| `space-4` | 16px | Standard component padding, mobile page margin |
| `space-5` | 20px | Card padding (compact) |
| `space-6` | 24px | Card padding (standard), section gaps |
| `space-8` | 32px | Section padding, desktop page margin |
| `space-10` | 40px | Large section gaps |
| `space-12` | 48px | Section separators |
| `space-16` | 64px | Major section breaks |
| `space-20` | 80px | Hero padding |
| `space-24` | 96px | Landing page sections |

### 5.2 Component Spacing

| Component | Internal Padding | External Margin |
|-----------|-----------------|-----------------|
| Button (sm) | 8px 12px | — |
| Button (md) | 12px 20px | — |
| Button (lg) | 16px 24px | — |
| Input field | 12px 16px | 8px below (to error message) |
| Card | 16px (mobile) / 24px (desktop) | 0 (grid gap handles spacing) |
| Product card | 12px | — |
| Modal | 24px | — |
| Alert/banner | 12px 16px | 16px below |
| Table cell | 12px 16px | — |
| Section | — | 48px top/bottom (mobile), 64px (desktop) |

### 5.3 Touch Target Spacing

Minimum **8px gap** between adjacent interactive elements on mobile to prevent mis-taps.

---

## 6. Buttons

### 6.1 Button Hierarchy

| Variant | Appearance | Usage | Max per view |
|---------|-----------|-------|--------------|
| **Primary** | Network Blue fill, white text | Main CTA: Add to Cart, Checkout, Submit | 1 per section |
| **Secondary** | White fill, navy border, navy text | Secondary actions: View Details, Compare | Unlimited |
| **Ghost** | Transparent, blue text | Tertiary: Cancel, Learn More | Unlimited |
| **Destructive** | Red fill, white text | Delete, Remove, Cancel Order | Confirmation required |
| **Trade** | Navy fill, white text + amber accent icon | Trade-specific: Apply for Account, Request Quote | Contextual |
| **Link** | Blue text, underline on hover | Inline navigation, "View all" | Unlimited |

### 6.2 Button Sizes

| Size | Height | Padding | Font | Min Width | Touch Target |
|------|--------|---------|------|-----------|--------------|
| **sm** | 36px | 8px 12px | 14px medium | 64px | 36px (desktop only) |
| **md** | 44px | 12px 20px | 14px medium | 80px | 44px ✓ |
| **lg** | 48px | 16px 24px | 16px medium | 120px | 48px ✓ |
| **xl** | 56px | 16px 32px | 16px semibold | 100% (mobile full-width) | 56px ✓ |

**Mobile rule:** Primary CTAs on product and checkout pages use `lg` or `xl` full-width.

### 6.3 Button States

| State | Primary | Secondary | Ghost |
|-------|---------|-----------|-------|
| **Default** | Blue fill | White + border | Transparent |
| **Hover** | Darker blue + shadow-sm | Light grey bg | Blue text underline |
| **Active/Pressed** | Darkest blue, shadow-none | Grey bg | Darker blue |
| **Focus** | Blue + focus ring (3px) | Border + focus ring | Focus ring |
| **Disabled** | 50% opacity, no pointer | 50% opacity | 50% opacity |
| **Loading** | Spinner replaces label, same dimensions | Same | Same |

### 6.4 Icon Buttons

| Size | Dimensions | Icon Size | Usage |
|------|-----------|-----------|-------|
| sm | 36 × 36px | 16px | Desktop toolbar actions |
| md | 44 × 44px | 20px | Mobile header actions, quantity +/- |
| lg | 48 × 48px | 24px | Primary mobile actions |

**Always include** `aria-label` for icon-only buttons.

### 6.5 Button Groups

- **Quantity selector:** Minus | Input | Plus — connected border group, 44px height
- **View toggle:** Grid | List — segmented control, 36px height (desktop catalog)
- **Checkout steps:** Numbered stepper, non-interactive for completed steps

---

## 7. Forms

### 7.1 Form Layout Principles

1. **Single column** on mobile — never side-by-side fields below 640px
2. **Labels above inputs** — not placeholder-only (accessibility requirement)
3. **Group related fields** — address block, payment block with visual separation
4. **Inline validation** — on blur, not on every keystroke
5. **Error recovery** — preserve entered values; focus first error on submit

### 7.2 Input Fields

| Property | Specification |
|----------|---------------|
| Height | 44px (touch-friendly) |
| Padding | 12px 16px |
| Border | 1px `--neutral-200` |
| Border radius | 6px |
| Background | `--neutral-50` (empty), `--neutral-0` (focused) |
| Font | 16px (prevents iOS zoom) |
| Focus | Border `--brand-accent`, focus ring shadow |
| Error | Border `--error`, error message below in `--error` 14px |
| Disabled | Background `--neutral-100`, text `--neutral-400` |

### 7.3 Input Types & Patterns

| Field | Type | Notes |
|-------|------|-------|
| Email | `email` | Autocomplete `email` |
| Password | `password` | Show/hide toggle, strength indicator on register |
| Phone | `tel` | Australian format hint: "04XX XXX XXX" |
| Postcode | `text` | 4 digits, numeric keyboard on mobile |
| State | Select dropdown | NSW, VIC, QLD, SA, WA, TAS, NT, ACT |
| ABN | `text` | 11 digits, auto-format XX XXX XXX XXX |
| Quantity | Number stepper | Min 1, max stock available |
| Search | Search with icon | Magnifying glass left, clear button right |
| Address | Autocomplete | Google Places / Loqate AU; manual entry fallback |

### 7.4 Select & Dropdown

- Height: 44px
- Chevron icon right-aligned
- Native select on mobile for OS-optimised picker
- Custom dropdown on desktop with keyboard navigation (arrow keys, Enter, Escape)

### 7.5 Checkbox & Radio

| Property | Value |
|----------|-------|
| Size | 20 × 20px (checkbox), 20px diameter (radio) |
| Touch target | 44 × 44px (include padding) |
| Checked colour | `--brand-accent` |
| Label gap | 12px |
| Label position | Right of control |

### 7.6 Form Sections (Checkout Example)

```
┌─────────────────────────────────────┐
│  1. Contact Information             │
│  ─────────────────────────────────  │
│  Email, Phone                         │
├─────────────────────────────────────┤
│  2. Shipping Address                │
│  ─────────────────────────────────  │
│  Address autocomplete, Suburb,        │
│  State, Postcode                      │
├─────────────────────────────────────┤
│  3. Delivery Method                 │
│  ─────────────────────────────────  │
│  Radio cards: Standard / Express /   │
│  Click & Collect                      │
├─────────────────────────────────────┤
│  4. Payment                         │
│  ─────────────────────────────────  │
│  Card element (Stripe), or Trade     │
│  Account / Bank Transfer options      │
└─────────────────────────────────────┘
```

### 7.7 Validation Messages

| Type | Colour | Icon | Example |
|------|--------|------|---------|
| Error | Red | Alert circle | "Please enter a valid Australian postcode" |
| Warning | Amber | Alert triangle | "This item has limited stock at your nearest warehouse" |
| Success | Green | Check circle | "Trade account discount applied" |
| Info | Blue | Info circle | "GST will be calculated at checkout" |

---

## 8. Product Cards

### 8.1 Card Anatomy

```
┌─────────────────────────────┐
│  ┌───────────────────────┐  │
│  │                       │  │
│  │    PRODUCT IMAGE      │  │  ← 1:1 aspect ratio
│  │    (with badges)      │  │
│  │                       │  │
│  └───────────────────────┘  │
│  BRAND NAME          (xs)   │  ← neutral-500, uppercase
│  Product Title              │  ← lg semibold, 2-line clamp
│  SKU: NET-UAP-AC-PRO        │  ← mono sm, neutral-500
│  ★★★★☆ (24)                │  ← optional, post-launch
│  $349.00 inc. GST           │  ← xl semibold
│  ── or ──                   │
│  $299.00 Trade              │  ← blue, with trade badge
│  ● In Stock                 │  ← green dot + label
│  ┌───────────────────────┐  │
│  │     Add to Cart       │  │  ← primary button, full-width
│  └───────────────────────┘  │
│  ♡  Compare  Quick View     │  ← ghost actions row
└─────────────────────────────┘
```

### 8.2 Card Variants

| Variant | Usage | Differences |
|---------|-------|-------------|
| **Standard** | Category/search grid | Full anatomy as above |
| **Compact** | Related products carousel | No SKU, smaller image, sm button |
| **List** | List view toggle (desktop) | Horizontal: image left, info right |
| **Trade** | Trade catalog | Trade price prominent, RRP struck through |
| **Out of stock** | Unavailable products | Greyed image overlay, "Notify Me" CTA |

### 8.3 Card Badges

| Badge | Colour | Position |
|-------|--------|----------|
| Sale | Red bg, white text | Top-left image |
| New | Blue bg, white text | Top-left image |
| Trade Only | Navy bg, amber text | Top-left image |
| Low Stock | Amber bg, dark text | Top-right image |
| Free Shipping | Green bg, white text | Below price |

**Max 2 badges** per card image to avoid clutter.

### 8.4 Card States

| State | Treatment |
|-------|-----------|
| Default | White card, shadow-sm, 6px radius |
| Hover (desktop) | shadow-md, subtle translateY(-2px), 200ms ease |
| Focus (keyboard) | Focus ring on card link |
| Loading | Skeleton: grey pulse blocks matching anatomy |
| In compare list | Blue border 2px, checkmark overlay |

### 8.5 Card Dimensions

| Breakpoint | Columns | Card Width | Image Size |
|------------|---------|------------|------------|
| Mobile | 2 | ~50% - gutter | ~160px |
| Tablet | 3 | ~33% | ~220px |
| Desktop | 4 | ~25% | ~280px |
| Wide | 4–5 | ~20–25% | ~280px |

---

## 9. Product Detail Pages

### 9.1 Page Structure

```
Mobile (single column):          Desktop (two column):
┌─────────────────────┐         ┌──────────────┬──────────────┐
│ Breadcrumb            │         │ Breadcrumb (full width)     │
├─────────────────────┤         ├──────────────┼──────────────┤
│ Image Gallery       │         │              │ Brand        │
│ (swipeable)         │         │   Gallery    │ Title        │
├─────────────────────┤         │   (55%)      │ SKU, Rating  │
│ Brand + Title       │         │              │ Price + GST  │
│ SKU + Rating        │         │              │ Stock Status │
│ Price Block         │         │              │ Variant Sel. │
│ Stock Status        │         │              │ Qty + ATC    │
│ Variant Selector    │         │              │ Trade CTA    │
│ Qty + Add to Cart   │         │              │ Delivery ETA │
│ [STICKY ATC BAR]    │         ├──────────────┴──────────────┤
├─────────────────────┤         │ Tabbed Content (full width)  │
│ Tabbed Content:     │         │ Description | Specs | Docs   │
│ Description         │         │ Reviews | Q&A                │
│ Specifications      │         ├──────────────────────────────┤
│ Downloads           │         │ Related Products carousel    │
│ Reviews             │         └──────────────────────────────┘
├─────────────────────┤
│ Related Products    │
└─────────────────────┘
```

### 9.2 Gallery

| Feature | Mobile | Desktop |
|---------|--------|---------|
| Primary image | Full-width, swipeable | Large main image |
| Thumbnails | Dot indicators below | Vertical strip left or horizontal below |
| Zoom | Pinch-to-zoom | Click to lightbox |
| Aspect ratio | 1:1 | 1:1 |
| Video | Play icon overlay if available | Same |

### 9.3 Price Block

```
$349.00
inc. GST
───────────────
RRP $399.00 (strikethrough, if on sale)

── Trade Account ──
$299.00 inc. GST
[Login for trade pricing] or [Trade price applied ✓]
```

### 9.4 Specifications Table

| Property | Value |
|----------|-------|
| Layout | Two-column table: label | value |
| Alternating rows | `--neutral-50` / white |
| Label column | 40% width, medium weight |
| Grouping | Collapsible sections: General, Network, Physical, Power |
| Mobile | Full-width, label above value stacked for complex specs |
| Compare | Checkbox per row to add to comparison (desktop) |

### 9.5 Sticky Add-to-Cart Bar (Mobile)

Appears when primary ATC button scrolls out of viewport.

| Element | Specification |
|---------|---------------|
| Height | 64px + safe-area-inset-bottom |
| Background | White, shadow-lg top border |
| Content | Product thumbnail (40px) + truncated title + price + ATC button |
| Z-index | Above content, below modals |

### 9.6 Trust & Compliance Strip

Below ATC button:
- ✓ Australian warranty
- ✓ GST tax invoice provided
- ✓ [X] delivery to [postcode]
- Secure checkout badge

---

## 10. Navigation

### 10.1 Header Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ [Announcement bar — promo, trade CTA, free shipping threshold]   │
├──────────────────────────────────────────────────────────────────┤
│ ☰  [LOGO]     [══════════ Search ══════════]    ♡  🛒(2)  👤   │
│                                                                  │
│ Networking | Tools | Electrical | Security | Brands | Trade ▾    │
└──────────────────────────────────────────────────────────────────┘
```

### 10.2 Mobile Header

| Element | Position | Size |
|---------|----------|------|
| Hamburger menu | Left | 44px touch target |
| Logo (logomark) | Centre-left | 32px height |
| Search icon | Right area | Opens full-screen search overlay |
| Wishlist | Right area | With badge count |
| Cart | Right area | With badge count |
| Account | Right area or in drawer | Avatar/icon |

**Header height:** 56px (compact) + announcement bar if present.
**Behaviour:** Sticky on scroll; shadow-sm appears after 10px scroll.

### 10.3 Desktop Header

| Element | Specification |
|---------|---------------|
| Logo | Full logo, 140px width max |
| Search | Centred, 480px max-width, typeahead dropdown |
| Utility nav | Wishlist, Cart (with count), Account dropdown |
| Category nav | Horizontal below header, mega-menu on hover |
| Trade link | Highlighted with amber dot or "Trade" badge |

**Header height:** 72px + 44px category bar = 116px total.

### 10.4 Mega Menu (Desktop)

```
┌─────────────────────────────────────────────────────────────┐
│ Networking                                                   │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ Switches     │ Routers      │ Wireless     │ Featured      │
│ • Managed    │ • Enterprise │ • Access Pts │ [Product img] │
│ • Unmanaged  │ • SOHO       │ • Controllers│ Ubiquiti      │
│ • PoE        │ • 4G/5G      │ • Bridges    │ UniFi 7       │
│              │              │              │ [Shop now →]  │
├──────────────┴──────────────┴──────────────┴───────────────┤
│ View all Networking →                                        │
└─────────────────────────────────────────────────────────────┘
```

- 4 columns maximum
- Category image optional in featured column
- Keyboard navigable (Tab, Arrow keys, Escape to close)
- Opens on hover (300ms delay) and click

### 10.5 Mobile Navigation Drawer

```
┌──────────────────────┐
│ ✕                    │
│ Hello, [Name] ▾      │  ← or "Sign in / Register"
├──────────────────────┤
│ 🔍 Search...         │
├──────────────────────┤
│ Networking         > │
│ Tools              > │
│ Electrical         > │
│ Security           > │
│ Brands             > │
├──────────────────────┤
│ ★ Trade Account      │  ← amber accent
│ 📋 Quick Order       │
│ 📞 Contact Sales     │
├──────────────────────┤
│ My Orders            │
│ My Quotes            │
│ Settings             │
└──────────────────────┘
```

- Slides from left, 85% viewport width, max 320px
- Subcategories drill down (push transition)
- Back button on subcategory views

### 10.6 Breadcrumbs

| Property | Value |
|----------|-------|
| Position | Below header, above page title |
| Separator | Chevron right, neutral-400 |
| Current page | neutral-900, not linked |
| Schema | BreadcrumbList JSON-LD |
| Mobile | Truncate middle segments: Home > … > Current |

### 10.7 Search

| Feature | Specification |
|---------|---------------|
| Mobile | Full-screen overlay, auto-focus input |
| Desktop | Inline with typeahead dropdown |
| Results preview | Top 5 products with image, name, price |
| Categories | Top 3 matching categories |
| Recent searches | Last 5 (logged-in: persisted) |
| Empty state | "Search 5,000+ products" + popular categories |
| No results | Suggest alternatives, link to contact |

---

## 11. Footer

### 11.1 Footer Structure

```
┌──────────────────────────────────────────────────────────────────┐
│  DARK BACKGROUND (--surface-dark)                                 │
│                                                                    │
│  [LOGO reversed]                                                   │
│                                                                    │
│  Shop          Trade & B2B     Support         Company            │
│  Networking    Trade Account   Contact Us      About A2Z          │
│  Tools         Bulk Order      Delivery        Careers            │
│  Electrical    Request Quote   Returns         Blog               │
│  Security      Price Lists     FAQs            Privacy Policy     │
│  Brands        Credit Terms    Track Order     Terms of Service   │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  ABN: XX XXX XXX XXX  │  GST Registered  │  🇦🇺 Australian Owned  │
├──────────────────────────────────────────────────────────────────┤
│  Payment icons: Visa, Mastercard, Amex, PayPal, Bank Transfer    │
├──────────────────────────────────────────────────────────────────┤
│  © 2025 A2Z Tools Pty Ltd. All rights reserved.                  │
│  [LinkedIn] [Facebook] [YouTube]                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 11.2 Mobile Footer

- Accordion sections (tap to expand/collapse)
- Single column link groups
- Payment icons in horizontal scroll if needed
- Sticky bottom nav replaces some footer links on mobile (see §12)

### 11.3 Footer Specifications

| Property | Value |
|----------|-------|
| Background | `--surface-dark` (#0F172A) |
| Text | `--neutral-300` (links), `--neutral-0` (headings) |
| Link hover | `--neutral-0` + underline |
| Padding | 48px top, 24px bottom (mobile); 64px top, 32px bottom (desktop) |
| Column gap | 32px (mobile stack), 48px (desktop grid) |
| Heading | `text-sm` semibold, uppercase, letter-spacing 0.05em |

### 11.4 Newsletter Signup (Footer)

- Email input + "Subscribe" button inline
- Copy: "Get trade tips, new products, and exclusive offers"
- Privacy note: "We respect your privacy. Unsubscribe anytime."
- Success state: green check + confirmation message

---

## 12. Mobile Design Rules

### 12.1 Core Principles

1. **Design for 375px first**, test at 320px minimum
2. **Thumb zone** — primary actions in bottom 60% of screen
3. **One task per screen** — checkout steps, filter panels as full-screen overlays
4. **44px minimum** touch targets on all interactive elements
5. **16px minimum** input font size (prevents iOS auto-zoom)
6. **No hover dependencies** — all hover states have tap equivalents

### 12.2 Mobile Bottom Navigation

Persistent on shop pages (hidden on checkout to reduce distraction).

```
┌────────┬────────┬────────┬────────┬────────┐
│  Home  │  Shop  │ Search │  Cart  │ Account  │
│  ⌂     │  ▦    │  🔍   │  🛒   │  👤     │
└────────┴────────┴────────┴────────┴────────┘
```

| Property | Value |
|----------|-------|
| Height | 56px + safe-area-inset-bottom |
| Background | White, border-top 1px neutral-200 |
| Active item | Network Blue icon + label |
| Cart badge | Red circle, white count |
| Z-index | 50 (below modals, above content) |

### 12.3 Mobile Interaction Patterns

| Pattern | Implementation |
|---------|---------------|
| Pull to refresh | Product listing, order history |
| Swipe actions | Cart item: swipe left to delete |
| Bottom sheet | Filters, sort, variant selector |
| Full-screen modal | Search, image gallery zoom |
| Infinite scroll | Product listing (with "Back to top" FAB) |
| FAB | "Back to top" — appears after 3 viewport scrolls |

### 12.4 Mobile Typography Adjustments

- Page titles: max `text-3xl` (30px)
- Reduce section padding to `space-8` (32px)
- Table data: horizontal scroll with scroll indicator shadow
- Spec tables: convert to stacked key-value pairs below 480px

### 12.5 Mobile Performance

- Hero images: max 800px wide WebP
- Product thumbnails: 400px WebP
- Lazy load below-fold images
- Skeleton screens for listing and PDP (not spinners)
- Target LCP < 2.5s on 4G

### 12.6 Mobile Checkout

- Progress stepper at top (4 steps: Cart → Shipping → Payment → Done)
- Full-width CTAs at bottom of each step
- Apple Pay / Google Pay prominent on payment step
- Auto-detect postcode for shipping estimate
- Order summary collapsible accordion above form

---

## 13. Desktop Design Rules

### 13.1 Core Principles

1. **Content max-width 1440px** — centred with auto margins
2. **Hover states** enhance discoverability but are not required
3. **Information density** — trade users expect more data visible without scrolling
4. **Keyboard navigation** — full tab order, visible focus rings
5. **Multi-column layouts** — leverage horizontal space for filters, sidebars

### 13.2 Desktop-Specific Features

| Feature | Specification |
|---------|---------------|
| Mega menu | Category navigation with subcategory columns |
| Filter sidebar | Sticky 280px left sidebar on catalog pages |
| Quick view | Modal product preview from catalog (without full navigation) |
| Comparison bar | Sticky bottom bar when comparing products (up to 4) |
| Multi-select cart | Checkbox per item for bulk actions |
| Hover product cards | Elevated shadow, quick action buttons appear |
| Keyboard shortcuts | `/` to focus search, `Esc` to close modals |

### 13.3 Desktop Catalog Layout

```
┌────────────┬───────────────────────────────────────────────────┐
│  FILTERS   │  [Sort ▾]  [Grid|List]  [48 results]              │
│  (sticky)  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐           │
│            │  │ Card │ │ Card │ │ Card │ │ Card │           │
│  Category  │  └──────┘ └──────┘ └──────┘ └──────┘           │
│  Brand     │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐           │
│  Price     │  │ Card │ │ Card │ │ Card │ │ Card │           │
│  In Stock  │  └──────┘ └──────┘ └──────┘ └──────┘           │
│  Specs     │                                                   │
│  [Clear]   │  [Load more] or pagination                       │
└────────────┴───────────────────────────────────────────────────┘
```

### 13.4 Desktop Checkout

- Two-column: form left (60%), sticky order summary right (40%)
- Summary shows line items, GST breakdown, shipping, total
- Payment step: card form inline (Stripe Elements)
- No bottom nav or distractions — minimal header (logo only)

---

## 14. Dashboard Design System

### 14.1 Account Dashboard Overview

Trade and business customers receive an enhanced dashboard; retail customers see a simplified version.

```
┌──────────────────────────────────────────────────────────────────┐
│  HEADER (simplified — logo, search, cart, account)                 │
├────────────┬─────────────────────────────────────────────────────┤
│            │  Welcome back, [Name]                               │
│  SIDEBAR   │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│            │  │ Orders    │ │ Quotes   │ │ Credit   │           │
│  Dashboard │  │ 12        │ │ 2 pending│ │ $5,000   │           │
│  Orders    │  └──────────┘ └──────────┘ └──────────┘           │
│  Quotes    │                                                     │
│  Invoices  │  Recent Orders                                      │
│  Addresses │  ┌─────────────────────────────────────────────┐  │
│  Wishlist  │  │ #A2Z-001  3 items  $1,240.00  Shipped  →   │  │
│  Settings  │  │ #A2Z-002  1 item   $349.00   Processing →  │  │
│  ────────  │  └─────────────────────────────────────────────┘  │
│  Trade     │                                                     │
│  Price List│  Quick Actions                                      │
│  Bulk Order│  [Reorder] [Request Quote] [Bulk Upload]           │
└────────────┴─────────────────────────────────────────────────────┘
```

### 14.2 Dashboard Sidebar

| Property | Value |
|----------|-------|
| Width | 240px (desktop), full-screen drawer (mobile) |
| Background | `--neutral-50` |
| Active item | White bg, blue left border 3px, semibold text |
| Item height | 44px |
| Icons | 20px, left of label, 12px gap |
| Sections | Separated by label: "Account", "Trade" (if applicable) |

### 14.3 Dashboard Cards

| Card Type | Content |
|-----------|---------|
| **Stat card** | Large number, label, optional trend arrow |
| **Order row** | Order number, date, item count, total, status badge, chevron |
| **Quote row** | Quote number, expiry date, total, status (pending/approved/expired) |
| **Invoice row** | Invoice number, date, amount, download PDF button |
| **Address card** | Label, formatted address, Edit / Delete actions |

### 14.4 Status Badges (Dashboard)

| Status | Background | Text |
|--------|-----------|------|
| Processing | Blue 50 | Blue 700 |
| Shipped | Amber 50 | Amber 700 |
| Delivered | Green 50 | Green 700 |
| Cancelled | Red 50 | Red 700 |
| Pending Quote | Amber 50 | Amber 700 |
| Quote Approved | Green 50 | Green 700 |
| Paid | Green 50 | Green 700 |
| Overdue | Red 50 | Red 700 |

### 14.5 Admin Dashboard (Staff)

Separate design layer on Django admin or custom admin SPA (Phase 2).

| Area | Key Widgets |
|------|-------------|
| Overview | Revenue today, orders pending, low stock alerts, trade applications |
| Orders | Filterable table, bulk status update, export CSV |
| Products | Inline edit, bulk price update, import CSV |
| Customers | Search, trade approval workflow, order history |
| Inventory | Stock levels by warehouse, adjustment form |

**Admin colour accent:** Use `--brand-secondary` (amber) to distinguish from customer-facing UI.

---

## 15. Icon System

### 15.1 Icon Library

**Primary:** Lucide Icons (MIT license, consistent with ShadCN UI)

**Supplementary:** Manufacturer logos (SVG assets), payment provider icons (official brand kits).

### 15.2 Icon Sizes

| Token | Size | Stroke | Usage |
|-------|------|--------|-------|
| `icon-xs` | 14px | 1.5px | Inline with small text, badges |
| `icon-sm` | 16px | 1.5px | Buttons (sm), table actions |
| `icon-md` | 20px | 2px | Default — nav, buttons, form icons |
| `icon-lg` | 24px | 2px | Feature highlights, empty states |
| `icon-xl` | 32px | 2px | Hero features, onboarding |

### 15.3 Icon Colour

| Context | Colour |
|---------|--------|
| Default | `--neutral-600` |
| On dark background | `--neutral-300` |
| Active/selected | `--brand-accent` |
| Destructive | `--error` |
| Success | `--success` |
| Disabled | `--neutral-300` |

### 15.4 Common Icons Mapping

| Action | Icon |
|--------|------|
| Search | `search` |
| Cart | `shopping-cart` |
| Wishlist | `heart` |
| Account | `user` |
| Menu | `menu` |
| Close | `x` |
| Add to cart | `shopping-bag` + "Add" label |
| Filter | `sliders-horizontal` |
| Sort | `arrow-up-down` |
| Grid view | `layout-grid` |
| List view | `list` |
| Delivery | `truck` |
| In stock | `check-circle` |
| Low stock | `alert-triangle` |
| Out of stock | `x-circle` |
| Download | `download` |
| Document/PDF | `file-text` |
| Compare | `git-compare` |
| Trade | `hard-hat` or `building-2` |
| Phone | `phone` |
| Email | `mail` |
| Secure | `shield-check` |
| External link | `external-link` |
| Chevron right | `chevron-right` |
| Back | `arrow-left` |

### 15.5 Icon Rules

- Always pair icon-only buttons with `aria-label`
- Decorative icons: `aria-hidden="true"`
- Minimum touch target 44px regardless of icon size
- Do not mix icon libraries within the same component
- Payment icons at consistent 32px height

---

## 16. Animation Guidelines

### 16.1 Motion Principles

1. **Purposeful** — Animation communicates state change, not decoration
2. **Fast** — Trade users value speed; animations never block interaction
3. **Subtle** — Professional tone; no bounces, wiggles, or excessive easing
4. **Respectful** — Honour `prefers-reduced-motion` system setting

### 16.2 Duration Tokens

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| `--duration-instant` | 0ms | — | Reduced motion fallback |
| `--duration-fast` | 100ms | ease-out | Button press, toggle |
| `--duration-normal` | 200ms | ease-out | Hover states, dropdowns |
| `--duration-moderate` | 300ms | ease-in-out | Drawer slide, modal fade |
| `--duration-slow` | 500ms | ease-in-out | Page transitions, carousel |

### 16.3 Standard Animations

| Animation | Properties | Duration | Trigger |
|-----------|-----------|----------|---------|
| Button hover | background-color, box-shadow | 200ms | Hover |
| Card hover lift | transform (translateY -2px), box-shadow | 200ms | Hover (desktop) |
| Dropdown open | opacity, transform (translateY -4px) | 200ms | Click |
| Mobile drawer | transform (translateX) | 300ms | Menu open |
| Bottom sheet | transform (translateY) | 300ms | Filter/sort open |
| Modal | opacity (backdrop), scale (content 0.95→1) | 300ms | Open |
| Toast notification | transform (translateY), opacity | 300ms | Auto-dismiss 5s |
| Skeleton pulse | opacity 0.5↔1 | 1500ms loop | Loading |
| Cart badge | scale (1→1.2→1) | 300ms | Item added |
| Accordion | height, opacity | 300ms | Expand/collapse |
| Tab indicator | transform (translateX) | 200ms | Tab switch |

### 16.4 Reduced Motion

When `prefers-reduced-motion: reduce`:
- Replace all transitions with instant state changes
- Disable carousel auto-play
- Disable parallax and scroll-linked animations
- Keep opacity fades at 0ms or remove entirely

### 16.5 Loading States

| Context | Pattern |
|---------|---------|
| Page load | Skeleton screens matching layout anatomy |
| Button action | Spinner inside button, disabled state |
| Image load | Blur-up placeholder (LQIP) → sharp image |
| Search | Inline spinner in search field |
| Infinite scroll | Skeleton cards at bottom |
| Form submit | Button loading + form fields disabled |

**Never** use full-page spinners except for initial app hydration.

---

## 17. Accessibility Standards

### 17.1 Compliance Target

**WCAG 2.1 Level AA** — mandatory for all public-facing pages.

| Criterion | Requirement |
|-----------|-------------|
| 1.1.1 Non-text content | Alt text on all product images; decorative images `alt=""` |
| 1.3.1 Info and relationships | Semantic HTML; headings in order; form labels associated |
| 1.4.3 Contrast (Minimum) | 4.5:1 text, 3:1 large text and UI components |
| 1.4.4 Resize text | Functional at 200% zoom |
| 1.4.11 Non-text contrast | 3:1 for UI boundaries, focus indicators, icons |
| 2.1.1 Keyboard | All functionality available via keyboard |
| 2.4.3 Focus order | Logical tab sequence |
| 2.4.7 Focus visible | 3px focus ring on all interactive elements |
| 2.5.5 Target size | 44 × 44px minimum touch targets |
| 3.3.1 Error identification | Errors described in text, linked to fields |
| 4.1.2 Name, role, value | ARIA attributes on custom components |

### 17.2 Focus Management

| Pattern | Behaviour |
|---------|-----------|
| Focus ring | 3px `--shadow-focus` (blue), 2px offset |
| Modal open | Trap focus inside modal; return focus on close |
| Drawer open | Trap focus in drawer |
| Skip link | "Skip to main content" — first focusable element |
| Route change | Move focus to `<h1>` of new page |
| Toast | `role="status"` `aria-live="polite"` |

### 17.3 Screen Reader Patterns

| Component | ARIA Pattern |
|-----------|-------------|
| Mobile nav | `role="dialog"` `aria-modal="true"` `aria-label="Navigation menu"` |
| Search overlay | `role="dialog"` `aria-label="Search"` |
| Product gallery | `role="region"` `aria-label="Product images"` |
| Tabs (PDP) | `role="tablist"`, `role="tab"`, `role="tabpanel"` |
| Cart count badge | `aria-label="2 items in cart"` |
| Stock status | `aria-label="In stock"` (not colour alone) |
| Price | `aria-label="$349.00 including GST"` |
| Loading | `aria-busy="true"` `aria-live="polite"` |
| Alerts | `role="alert"` for errors; `role="status"` for success |

### 17.4 Colour Independence

Never convey information by colour alone:

| Information | Colour + Additional Indicator |
|-------------|------------------------------|
| In stock | Green dot + "In Stock" text |
| Low stock | Amber triangle icon + "Only 3 left" text |
| Out of stock | Red X icon + "Out of Stock" text |
| Sale price | Red text + "Sale" badge + strikethrough RRP |
| Required field | Asterisk + "(required)" in label |
| Error field | Red border + error icon + error message text |

### 17.5 Form Accessibility

- Every input has a visible `<label>` (not placeholder-only)
- `aria-required="true"` on required fields
- `aria-invalid="true"` + `aria-describedby` pointing to error message
- `autocomplete` attributes on address and payment fields
- Group related fields with `<fieldset>` and `<legend>`
- Error summary at top of form on submit (linked to fields)

### 17.6 Testing Checklist

| Test | Tool / Method |
|------|---------------|
| Automated scan | axe-core in CI, Lighthouse accessibility audit |
| Keyboard navigation | Manual tab-through of all flows |
| Screen reader | VoiceOver (macOS/iOS), NVDA (Windows) |
| Colour contrast | Stark, WebAIM Contrast Checker |
| Zoom | 200% browser zoom — no horizontal scroll, no clipped content |
| Reduced motion | macOS/iOS setting enabled — verify no motion |
| Mobile touch | 44px targets verified on 375px viewport |

### 17.7 Accessibility Targets

| Metric | Target |
|--------|--------|
| Lighthouse Accessibility score | ≥ 95 |
| axe-core violations | 0 critical, 0 serious |
| Keyboard flow completion | 100% of core flows (browse, cart, checkout, account) |

---

## Appendix

### A. Component Checklist (ShadCN Mapping)

| Design System Component | ShadCN Base |
|--------------------------|-------------|
| Button | `Button` |
| Input | `Input` |
| Select | `Select` |
| Checkbox | `Checkbox` |
| Radio group | `RadioGroup` |
| Card | `Card` |
| Badge | `Badge` |
| Dialog/Modal | `Dialog` |
| Sheet (drawer) | `Sheet` |
| Tabs | `Tabs` |
| Table | `Table` |
| Toast | `Sonner` |
| Dropdown | `DropdownMenu` |
| Accordion | `Accordion` |
| Breadcrumb | `Breadcrumb` |
| Skeleton | `Skeleton` |
| Avatar | `Avatar` |
| Separator | `Separator` |
| Tooltip | `Tooltip` |
| Pagination | `Pagination` |

### B. Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-base` | 0 | Default content |
| `z-dropdown` | 10 | Dropdowns, tooltips |
| `z-sticky` | 20 | Sticky header, ATC bar |
| `z-bottom-nav` | 30 | Mobile bottom navigation |
| `z-drawer` | 40 | Side drawers, filter sheets |
| `z-modal` | 50 | Modals, dialogs |
| `z-toast` | 60 | Toast notifications |
| `z-max` | 70 | Critical overlays |

### C. Document References

| Document | Location |
|----------|----------|
| Project Master Plan | `/docs/PROJECT_MASTER_PLAN.md` |
| Database Plan | `/docs/DATABASE_PLAN.md` |

---

*Document Version: 1.0*
*Last Updated: June 2025*
*Author: Senior UI/UX Designer*
*Status: Approved for Phase 1 Implementation*
