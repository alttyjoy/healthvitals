# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons + DOMPurify
- **Backend**: FastAPI (Python) + MongoDB + APScheduler
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (live integration with test keys)
- **Design**: Sky Blue (#0EA5E9) + Emerald (#10B981) palette, Outfit + Figtree fonts, dark mode support

## What's Been Implemented

### Phase 1-5 (April 10-24, 2026)
- Full MVP, Auth, Dashboard, Tracker, Charts, Export, Plans, Admin
- Razorpay, PayU.In, Dark mode, Multilingual, Shared reports, Referral System
- Content Pages, Admin SMTP/Reminder config, Forgot Password, 8 FAQs
- Responsive Landing, Admin User CRUD, Coupon System, Color Refresh

### Phase 7 — Code Quality Fixes (May 29, 2026)
- **XSS Fix**: ContentPage.js now uses DOMPurify to sanitize HTML before rendering
- **Hardcoded Secrets**: Moved admin2 credentials to .env (ADMIN2_EMAIL, ADMIN2_PASSWORD), all test files use os.environ.get()
- **React Hook Dependencies**: Fixed stale closures in Billing, AdminPanel, DailyTracker, Settings with proper dependency arrays
- **Empty Error Handlers**: Added console.error logging to all previously empty catch blocks in AuthContext, Settings
- **Array Index Keys**: Replaced index-based React keys with stable identifiers (title, question text, vital_key) in Landing, Dashboard, Billing, AdminPanel

## Pricing (INR)
- Free: ₹0 (2 vitals, 7-day history, CSV only)
- Standard: ₹299/mo or ₹2,999/yr (6 vitals, full history, CSV+PDF, sharing)
- Premium: ₹499/mo or ₹4,999/yr (12 vitals, unlimited, all features)

## Prioritized Backlog
### P1
- [ ] Stripe payment gateway integration (3rd gateway option)

### P2
- [ ] PDF/CSV export verification (watermarking, chart inclusion)
- [ ] Push notification architecture (Firebase FCM)
- [ ] Advanced analytics (period comparison, trend arrows)

### P3
- [ ] Mobile app API hardening
- [ ] AI-powered health insights
- [ ] Device sync readiness
- [ ] Break down AdminPanel.js (787 lines) into sub-components
- [ ] Break down Settings.js (403 lines) into sub-components
- [ ] Break down server.py get_insights/generate_export into helpers
