# VitalTrack - Health Vitals Tracking SaaS Platform

## Product Overview
A SaaS platform for daily tracking, monitoring, visualizing, exporting, and managing 12 health vitals with freemium subscription model.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Shadcn/UI + Phosphor Icons
- **Backend**: FastAPI (Python) + MongoDB
- **Auth**: JWT with httpOnly cookies, role-based access
- **Design**: Earthy palette (deep green #2D4A3E, terracotta #D96C4E, stone #FAFAF9), Outfit + Inter fonts

## User Personas
1. **Free User**: Tracks 2 vitals, 7-day chart history, CSV export only
2. **Standard Subscriber** (₹299/mo): 6 vitals, 1-year history, CSV+PDF, sharing
3. **Premium Subscriber** (₹599/mo): All 12 vitals, unlimited history, all features
4. **Admin**: Full platform management, user/plan control, analytics

## Core Requirements
- 12 health vitals tracking (Blood Glucose, Blood Oxygen, Blood Pressure, BMI, Body Temperature, Heart Rate, Respiratory Rate, Sleep Duration, Physical Activity, Waist Circumference, Weight, Hydration)
- Spreadsheet-style daily tracker with inline editing
- Tailored chart visualizations per vital type
- CSV/PDF export with plan gating
- Subscription plan management (Free/Standard/Premium)
- Admin panel with user management, analytics, audit logs
- Rule-based health insights

## What's Been Implemented (April 10, 2026)
### Backend (34 API endpoints)
- Auth: register, login, logout, me, refresh, forgot-password, reset-password
- Vitals: types, enabled, toggle
- Entries: CRUD, bulk save, delete
- Charts: data per vital with stats
- Insights: rule-based health analysis
- Plans: list, subscription change
- Exports: CSV and PDF generation
- Reminders: CRUD
- Shared Reports: create, list, view (public), revoke
- Admin: dashboard stats, users (CRUD + search), plans management, analytics

### Frontend (10 pages)
- Landing page (hero, features, pricing, FAQ, CTA, footer)
- Login / Register
- Dashboard (overview cards, insights, quick actions, vitals summary)
- Daily Tracker (spreadsheet-style with sticky headers, inline editing, status colors, bulk save)
- Charts & Trends (line/bar/area/dual-line charts, date range filters, stats)
- Reports/Export (CSV/PDF with vital & date selection)
- Billing (plan cards, upgrade/downgrade)
- Settings (profile management, vital enable/disable with plan limits)
- Admin Panel (overview, users management, analytics with charts)

### Design System
- Earthy warm palette (green, terracotta, stone)
- Outfit headings, Inter body text
- Phosphor Icons (duotone)
- Shadcn/UI components customized

## Prioritized Backlog
### P0 (Critical)
- [ ] Payment gateway integration (Razorpay, PayU.In, Stripe) - currently MOCKED
- [ ] Email/SMTP system for reminders and notifications

### P1 (Important)
- [ ] Shared reports with secure URLs and password protection
- [ ] Push notification architecture (Firebase FCM ready)
- [ ] Dark mode toggle
- [ ] Multilingual support (English, Hindi, Telugu)

### P2 (Nice to have)
- [ ] Blog/content management pages
- [ ] Admin SMTP settings management
- [ ] Weekly summary digest emails
- [ ] Advanced analytics (period comparison, trend arrows)
- [ ] Mobile app API hardening (versioned routes, pagination)
- [ ] AI-powered health insights
- [ ] Device sync readiness

## Next Tasks
1. Integrate Razorpay payment gateway (needs API keys)
2. Set up SMTP for email notifications
3. Add dark mode toggle
4. Build shared reports with secure URL generation
5. Add multilingual support
