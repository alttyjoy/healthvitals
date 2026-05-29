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
├── server.py        # Slim orchestrator (~130 lines) - app, CORS, startup/shutdown, router mounting
├── config.py        # DB, JWT, constants (VITAL_TYPES, PLANS, TRANSLATIONS, CONTENT_PAGES), payment clients, VAPID, scheduler
├── models.py        # All Pydantic request models
├── utils.py         # Auth helpers, email, serialization, reminders
├── routes/
│   ├── auth.py      # Auth: register, login, logout, me, refresh, forgot/reset password, profile
│   ├── vitals.py    # Vitals: types, enabled, toggle, entries CRUD, charts, insights, reminders
│   ├── exports.py   # CSV & PDF export generation, export list
│   ├── sharing.py   # Shared reports: create, list, view (with/without password), revoke
│   ├── referral.py  # Referral info, apply referral code
│   ├── push.py      # Push notifications: VAPID key, subscribe, unsubscribe, status, admin send/stats
│   ├── content.py   # Public content pages, translations, languages, blog CRUD
│   ├── payments.py  # Plans, subscription, Razorpay (order/verify/webhook), PayU (initiate/callback)
│   ├── admin.py     # Admin: dashboard, users CRUD, analytics, SMTP, reminders, content pages, coupons
│   └── sync.py      # Device sync: register-device, pull, push, devices list, remove device
```

## Frontend Architecture (Decomposed)
```
/app/frontend/src/
├── pages/
│   ├── AdminPanel.js (200 lines) → imports UserManagement, CouponManagement, AdminSettings, ContentManagement
│   ├── Settings.js (340 lines) → imports ReferralSection, PushNotificationSettings
│   └── ... (other pages unchanged)
├── components/
│   ├── admin/       # UserManagement, CouponManagement, AdminSettings, ContentManagement
│   ├── settings/    # ReferralSection, PushNotificationSettings
│   └── ui/          # Shadcn components
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
- Array Index Keys replaced with stable identifiers

### Phase 8 — Decomposition & Device Sync (May 29, 2026)
- **Backend decomposed**: server.py 1954 lines → 10 route modules + config + models + utils (~130 line orchestrator)
- **Frontend decomposed**: AdminPanel.js 839→200 lines (4 sub-components), Settings.js 427→340 lines (2 sub-components)
- **Push Notifications**: Frontend fetches VAPID key from backend API, toggle UI in Settings
- **CSV/PDF Export**: Verified end-to-end with summary statistics, watermarking
- **Device Sync API**: New endpoints for multi-device support (register, pull, push, list, remove)
- **Testing**: 25/25 backend tests, 100% frontend UI tests passed (iteration_7)

## Pricing (INR)
- Free: ₹0 (2 vitals, 7-day history, CSV only)
- Standard: ₹299/mo or ₹2,999/yr (6 vitals, full history, CSV+PDF, sharing)
- Premium: ₹499/mo or ₹4,999/yr (12 vitals, unlimited, all features)

## Prioritized Backlog
### P1
- [ ] Stripe payment gateway integration (3rd gateway option)

### P2
- [ ] Advanced analytics (period comparison, trend arrows)
- [ ] AI-powered health insights

### P3
- [ ] Mobile app API hardening (React Native / Flutter)
- [ ] Migrate to FastAPI lifespan context manager
- [ ] Replace browser-default time inputs with shadcn components
- [ ] Standardize timestamp storage format across DB collections
