# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons
- **Backend**: FastAPI (Python) + MongoDB
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (live integration with test keys)
- **Design**: Earthy palette, Outfit + Inter fonts, dark mode support

## What's Been Implemented

### Phase 1 (April 10, 2026)
- Full MVP: Auth, Dashboard, Tracker, Charts, Export, Plans, Admin

### Phase 2 (April 10, 2026)
- Premium price updated to ₹499/month
- Razorpay payment gateway integrated (order creation, verification, webhook)
- Dark mode toggle
- Multilingual support (English, Hindi, Telugu)
- Shared reports with password-protected secure URLs
- Plan upgrade/downgrade with Razorpay checkout for paid plans
- Direct plan switch for free plan downgrade

### Phase 3 (April 10, 2026)
- **Content Pages**: Terms of Service, Privacy Policy, Refund Policy, About - rendered via `/page/:pageKey` route
- **PayU.In Payment Gateway**: Frontend gateway selector (Razorpay/PayU toggle), PayU form POST redirect flow, callback handling with URL params
- **Referral System UI**: Referral code display with copy, referral stats, apply referral code input in Settings page
- **Admin SMTP Configuration**: New Settings tab in Admin Panel with full SMTP form (Host, Port, Username, Password, From Email, From Name, TLS toggle)
- **Footer Legal Links**: Landing page footer now has Terms, Privacy, Refunds, About navigation links

## Pricing (INR)
- Free: ₹0 (2 vitals, 7-day history, CSV only)
- Standard: ₹299/mo or ₹2,999/yr (6 vitals, full history, CSV+PDF, sharing)
- Premium: ₹499/mo or ₹4,999/yr (12 vitals, unlimited, all features)

## Prioritized Backlog
### P1
- [ ] Stripe payment gateway integration (3rd gateway option)
- [ ] Email Reminder system (APScheduler + saved SMTP config for missed tracking notifications)
- [ ] Admin Content Management UI (CRUD for blog posts, FAQs, legal policies)
- [ ] PDF/CSV export verification (watermarking, chart inclusion)

### P2
- [ ] Push notification architecture (Firebase FCM)
- [ ] Advanced analytics (period comparison, trend arrows)
- [ ] Mobile app API hardening
- [ ] AI-powered health insights
- [ ] Device sync readiness
