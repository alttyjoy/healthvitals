# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons + DOMPurify
- **Backend**: FastAPI (Python) + MongoDB + APScheduler — Modular route architecture
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (mode-aware dynamic key loading, test/live toggle)
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
│   ├── vitals.py    # Vitals, entries, charts (stats+comparison), insights (trends)
│   ├── exports.py   # CSV & PDF export
│   ├── sharing.py   # Shared reports CRUD
│   ├── referral.py  # Referral system
│   ├── push.py      # Push notifications
│   ├── content.py   # Public content, translations, blog
│   ├── payments.py  # Plans, subscription, Razorpay, PayU (mode-aware dynamic keys)
│   ├── admin.py     # Admin: dashboard, users, analytics, SMTP, reminders, content, coupons, payment settings, payment history
│   └── sync.py      # Device sync
```

## What's Been Implemented

### Phase 1-7 (April-May 2026)
- Full MVP, Auth, Dashboard, Tracker, Charts, Export, Plans, Admin
- Razorpay, PayU.In, Dark mode, Multilingual, Shared reports, Referral System
- Content Pages, Admin SMTP/Reminder, Forgot Password, Coupons, Color Refresh
- XSS Fix, Code Quality

### Phase 8 — Decomposition & Device Sync (May 2026)
- Backend: 1954-line monolith → 10 route modules
- Frontend: AdminPanel 839→200, Settings 427→340 lines
- Push Notifications, CSV/PDF Export, Device Sync API

### Phase 9 — Advanced Analytics (May 2026)
- Enhanced insights with change_percent, previous_average, min, max, trend
- Charts period comparison, Dashboard trend arrows

### Phase 10 — Security & Payment Fixes (July-Aug 2026)
- 229→7 npm vulnerabilities fixed (remaining 7 are dev-only low/moderate)
- 4 payment gateway bugs fixed
- Admin Payment Settings UI with masked secrets

### Phase 11 — Test/Live Mode & Payment History (Aug 2026)
- **Test/Live Mode Toggle**: Switch between sandbox and production environments
  - Separate key storage per mode (test bucket + live bucket)
  - PayU URL auto-selected by mode (test.payu.in vs secure.payu.in)
  - Visual indicators: blue "Test Mode" vs red "Live Mode" with safety messaging
  - Keys switch instantly when toggling modes
- **Payment History Tab**: New "Payments" tab in Admin Panel
  - Aggregates transactions from both Razorpay and PayU collections via $unionWith
  - Columns: User, Gateway (color-coded badges), Plan, Amount, Order ID, Status, Date
  - Correct server-side pagination with skip/limit
  - Status badges: success (green), initiated (amber), failed (red)
  - Refresh button, pagination controls
- Testing: 11/11 backend, 100% frontend UI

## Pricing (INR)
- Free: ₹0 (2 vitals, 7-day history, CSV only)
- Standard: ₹299/mo or ₹2,999/yr (6 vitals, full history, CSV+PDF, sharing)
- Premium: ₹499/mo or ₹4,999/yr (12 vitals, unlimited, all features)

## Prioritized Backlog
### P1
- [ ] Stripe payment gateway integration (3rd gateway option)

### P2
- [ ] AI-powered health insights
- [ ] Weekly health digest emails

### P3
- [ ] Mobile app API hardening (React Native / Flutter)
