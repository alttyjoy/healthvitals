# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons
- **Backend**: FastAPI (Python) + MongoDB + APScheduler
- **Auth**: JWT with httpOnly cookies, role-based access
- **Payments**: Razorpay, PayU.In (live integration with test keys)
- **Design**: Earthy palette, Outfit + Inter fonts, dark mode support

## What's Been Implemented

### Phase 1 (April 10, 2026)
- Full MVP: Auth, Dashboard, Tracker, Charts, Export, Plans, Admin

### Phase 2 (April 10, 2026)
- Premium price updated to ₹499/month
- Razorpay payment gateway integrated
- Dark mode toggle
- Multilingual support (English, Hindi, Telugu)
- Shared reports with password-protected secure URLs
- Plan upgrade/downgrade with Razorpay checkout

### Phase 3 (April 10, 2026)
- Content Pages: Terms, Privacy, Refund, About
- PayU.In Payment Gateway frontend with gateway selector
- Referral System UI in Settings
- Admin SMTP Configuration form

### Phase 4 (April 17, 2026)
- **New Admin User**: mohanv44@gmail.com / India@1947 as super_admin
- **Sidebar Rename**: "Dashboard" → "Home"
- **8 FAQs**: Expanded from 4 to 8 health-relevant questions
- **Forgot Password**: Full flow — Login page link → /forgot-password → email submit → token-based reset at /reset-password
- **Responsive Design**: Landing page mobile hamburger menu, responsive hero/features/pricing/CTA/footer
- **Email Reminder System**: APScheduler cron job, reads SMTP config from DB, sends HTML reminders to users who missed daily tracking. Admin can enable/disable, set time, trigger manually.
- **Admin Content Management**: Full CRUD for content pages (blog, legal, custom). Built-in pages protected from deletion but can be overridden. Dialog-based editor with markdown support.

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

## Notes
- Email reminders are FUNCTIONAL but require SMTP configuration in Admin Panel → Settings tab to actually send emails. Without SMTP config, the system logs warnings.
- Forgot Password token is logged on server (not emailed) until SMTP is configured.
