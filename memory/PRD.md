# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons + DOMPurify
- **Backend**: FastAPI (Python) + MongoDB + APScheduler — Modular route architecture
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (dynamic key loading from DB, .env fallback)
- **Design**: Sky Blue (#0EA5E9) + Emerald (#10B981) palette, Outfit + Figtree fonts, dark mode support

## Backend Architecture (Decomposed)
```
/app/backend/
├── server.py        # Slim orchestrator (~130 lines)
├── config.py        # DB, JWT, constants, payment clients, VAPID, scheduler
├── models.py        # All Pydantic request models
├── utils.py         # Auth helpers, email, serialization, reminders
├── routes/
│   ├── auth.py      # Auth endpoints
│   ├── vitals.py    # Vitals: types, toggle, entries, charts (stats+comparison), insights (trends+comparison)
│   ├── exports.py   # CSV & PDF export
│   ├── sharing.py   # Shared reports CRUD
│   ├── referral.py  # Referral system
│   ├── push.py      # Push notifications
│   ├── content.py   # Public content, translations, blog
│   ├── payments.py  # Plans, subscription, Razorpay, PayU (dynamic DB key loading)
│   ├── admin.py     # Admin: dashboard, users, analytics, SMTP, reminders, content, coupons, PAYMENT SETTINGS
│   └── sync.py      # Device sync
```

## What's Been Implemented

### Phase 1-7 (April-May 2026)
- Full MVP, Auth, Dashboard, Tracker, Charts, Export, Plans, Admin
- Razorpay, PayU.In, Dark mode, Multilingual, Shared reports, Referral System
- Content Pages, Admin SMTP/Reminder, Forgot Password, Coupons
- XSS Fix, Code Quality, Color Refresh

### Phase 8 — Decomposition & Device Sync (May 2026)
- Backend: 1954-line monolith → 10 route modules
- Frontend: AdminPanel 839→200, Settings 427→340 lines
- Push Notifications, CSV/PDF Export verified, Device Sync API

### Phase 9 — Advanced Analytics (May 2026)
- Enhanced /api/insights with change_percent, previous_average, min, max, trend
- Enhanced /api/charts with stats, previous_stats, compare toggle
- Dashboard trend arrows, Charts period comparison overlay

### Phase 10 — Security & Payment Fixes (July-Aug 2026)
- **229→0 npm vulnerabilities** fixed via yarn resolutions (7 low/moderate dev-only remain)
- **4 payment gateway bugs fixed**: PayU env var mismatch, Razorpay verify endpoint, PayU response field names, PayU callback flow
- **Admin Payment Settings UI**: New section in Admin > Settings to manage Razorpay/PayU keys from UI
  - Secrets masked on read (********), preserved on write if unchanged
  - Dynamic key loading: DB settings → .env fallback
  - "Configured" badges check both key+secret present
  - Eye/EyeSlash toggle for secret visibility
  - Razorpay client auto-reinitialized on save

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
