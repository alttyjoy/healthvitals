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
- Premium ₹499/month, Razorpay, Dark mode, Multilingual, Shared reports

### Phase 3 (April 10, 2026)
- Content Pages, PayU.In, Referral System UI, Admin SMTP Config

### Phase 4 (April 17, 2026)
- New Admin (mohanv44@gmail.com), Sidebar "Home", 8 FAQs, Forgot Password, Responsive Landing, Email Reminders, Admin Content Management

### Phase 5 (April 17, 2026)
- **Admin User CRUD**: Full Add/Edit/Delete users from Admin Panel → Users tab
  - Add User: Name, Email, Password, Role (User/Admin), Plan selector
  - Edit User: Update name, role, plan (email read-only)
  - Delete User: Confirm dialog, cascade deletes entries/exports/reports, self-delete protection
  - Backend: POST/PUT/DELETE `/api/admin/users` with validation

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
- Email reminders require SMTP configuration in Admin Panel → Settings tab
- Forgot Password token logged on server until SMTP is configured
- Admin roles: super_admin (full access), user (standard access)
