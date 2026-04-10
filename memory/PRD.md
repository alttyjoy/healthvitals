# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons
- **Backend**: FastAPI (Python) + MongoDB
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay (live integration with test keys)
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

## Pricing (INR)
- Free: ₹0 (2 vitals, 7-day history, CSV only)
- Standard: ₹299/mo or ₹2,999/yr (6 vitals, full history, CSV+PDF, sharing)
- Premium: ₹499/mo or ₹4,999/yr (12 vitals, unlimited, all features)

## Prioritized Backlog
### P0
- [ ] PayU.In and Stripe payment gateway integration
- [ ] Email/SMTP system for reminders and notifications

### P1
- [ ] Push notification architecture (Firebase FCM)
- [ ] Blog/content management pages
- [ ] Advanced analytics (period comparison, trend arrows)

### P2
- [ ] Mobile app API hardening
- [ ] AI-powered health insights
- [ ] Device sync readiness
