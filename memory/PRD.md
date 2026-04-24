# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons
- **Backend**: FastAPI (Python) + MongoDB + APScheduler
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (live integration with test keys)
- **Design**: Sky Blue (#0EA5E9) + Emerald (#10B981) palette, Outfit + Figtree fonts, dark mode support

## What's Been Implemented

### Phase 1-4 (April 10-17, 2026)
- Full MVP, Auth, Dashboard, Tracker, Charts, Export, Plans, Admin
- Razorpay, PayU.In, Dark mode, Multilingual, Shared reports
- Content Pages, Referral System, Admin SMTP/Reminder config
- Forgot Password, 8 FAQs, Responsive Landing, Admin User CRUD

### Phase 6 (April 24, 2026)
- **Color Scheme Refresh**: Complete rebrand from muddy olive/earthy tones to modern Sky Blue + Emerald palette
  - Primary: #0EA5E9 (Sky Blue), Hover: #0284C7
  - Accent: #10B981 (Emerald Green)
  - Background: #F8FAFC, Cards: White, Borders: #E2E8F0
  - Text: #0F172A (primary), #64748B (secondary)
  - Danger: #EF4444
  - CTA sections use gradient (from-sky-500 to-sky-600) with blue glow shadows
  - Glassmorphism nav header (backdrop-blur-xl)
  - Body font changed from Inter to Figtree
  - Updated 19 source files (all pages + components + CSS)

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
