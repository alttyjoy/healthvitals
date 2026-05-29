# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons + DOMPurify
- **Backend**: FastAPI (Python) + MongoDB + APScheduler — Modular route architecture
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (live integration with test keys)
- **Design**: Sky Blue (#0EA5E9) + Emerald (#10B981) palette, Outfit + Figtree fonts, dark mode support

## Backend Architecture (Decomposed)
```
/app/backend/
├── server.py        # Slim orchestrator (~130 lines)
├── config.py        # DB, JWT, constants, payment clients, VAPID, scheduler
├── models.py        # All Pydantic request models
├── utils.py         # Auth helpers, email, serialization, reminders
├── routes/
│   ├── auth.py      # Auth: register, login, logout, me, refresh, forgot/reset password, profile
│   ├── vitals.py    # Vitals: types, enabled, toggle, entries CRUD, charts (with stats+comparison), insights (with trends+comparison)
│   ├── exports.py   # CSV & PDF export generation
│   ├── sharing.py   # Shared reports CRUD
│   ├── referral.py  # Referral system
│   ├── push.py      # Push notifications (VAPID, subscribe, status, admin send)
│   ├── content.py   # Public content pages, translations, blog
│   ├── payments.py  # Plans, subscription, Razorpay, PayU
│   ├── admin.py     # Admin: dashboard, users CRUD, analytics, SMTP, reminders, content, coupons
│   └── sync.py      # Device sync: register, pull, push, devices
```

## What's Been Implemented

### Phase 1-5 (April 10-24, 2026)
- Full MVP, Auth, Dashboard, Tracker, Charts, Export, Plans, Admin
- Razorpay, PayU.In, Dark mode, Multilingual, Shared reports, Referral System
- Content Pages, Admin SMTP/Reminder config, Forgot Password, 8 FAQs
- Responsive Landing, Admin User CRUD, Coupon System, Color Refresh

### Phase 7 — Code Quality Fixes (May 29, 2026)
- XSS Fix (DOMPurify), Hardcoded Secrets moved to .env
- React Hook Dependencies fixed, Empty Error Handlers filled

### Phase 8 — Decomposition & Device Sync (May 29, 2026)
- Backend decomposed: 1954-line monolith → 10 route modules
- Frontend decomposed: AdminPanel 839→200 lines, Settings 427→340 lines
- Push Notifications: VAPID key from API, toggle UI in Settings
- CSV/PDF Export: Verified end-to-end
- Device Sync API: register, pull, push, list, remove

### Phase 9 — Advanced Analytics (May 29, 2026)
- **Enhanced /api/insights**: Returns `change_percent`, `previous_average`, `min`, `max`, `trend` per vital (this week vs last week)
- **Enhanced /api/charts/{vital_key}**: Returns `stats`, `previous_stats`, `change_percent`, `trend`; supports `compare=true` to get `previous_entries` for overlay
- **Dashboard trend arrows**: Color-coded (context-aware: rising=bad for BP/glucose, good for sleep/activity), % change, prev avg, min-max range per insight
- **Dashboard vitals sidebar**: Inline trend arrows with % change next to today's value
- **Charts Compare toggle**: Overlays previous period as dashed ghost line on chart
- **Charts enhanced stat cards**: Current + previous values with colored % change pill badges
- **Trend color logic**: Per-vital direction mapping (RISING_IS_GOOD set for sleep, activity, hydration, blood_oxygen)

## Pricing (INR)
- Free: ₹0 (2 vitals, 7-day history, CSV only)
- Standard: ₹299/mo or ₹2,999/yr (6 vitals, full history, CSV+PDF, sharing)
- Premium: ₹499/mo or ₹4,999/yr (12 vitals, unlimited, all features)

## Prioritized Backlog
### P1
- [ ] Stripe payment gateway integration (3rd gateway option)

### P2
- [ ] AI-powered health insights

### P3
- [ ] Mobile app API hardening (React Native / Flutter)
- [ ] Migrate to FastAPI lifespan context manager
- [ ] Replace browser-default time inputs with shadcn components
