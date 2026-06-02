from dotenv import load_dotenv
from pathlib import Path
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import razorpay

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
JWT_ALGORITHM = "HS256"

# Razorpay
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    logger.info("Razorpay client initialized")

# VAPID for Push Notifications
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "").replace("\\n", "\n")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_EMAIL = os.environ.get("VAPID_EMAIL", "mailto:admin@vitaltrack.in")

# Scheduler
scheduler = AsyncIOScheduler()

# ==================== CONSTANTS ====================
VITAL_TYPES = [
    {"key": "blood_glucose", "name": "Blood Glucose", "unit": "mg/dL", "min": 10, "max": 600, "normal_min": 70, "normal_max": 140, "chart_type": "line", "category": "metabolic"},
    {"key": "blood_oxygen", "name": "Blood Oxygen", "unit": "%", "min": 10, "max": 100, "normal_min": 95, "normal_max": 100, "chart_type": "area", "category": "respiratory"},
    {"key": "blood_pressure", "name": "Blood Pressure", "unit": "mmHg", "min": 10, "max": 500, "normal_min": 80, "normal_max": 120, "chart_type": "dual_line", "category": "cardiovascular", "has_dual_value": True, "value2_label": "Diastolic", "value2_min": 40, "value2_max": 150, "value2_normal_min": 60, "value2_normal_max": 90},
    {"key": "bmi", "name": "BMI", "unit": "kg/m2", "min": 5, "max": 60, "normal_min": 18, "normal_max": 24, "chart_type": "line", "category": "body"},
    {"key": "body_temperature", "name": "Body Temperature", "unit": "F", "min": 90, "max": 110, "normal_min": 97, "normal_max": 99.5, "chart_type": "line", "category": "general"},
    {"key": "heart_rate", "name": "Heart Rate", "unit": "bpm", "min": 10, "max": 250, "normal_min": 72, "normal_max": 100, "chart_type": "line", "category": "cardiovascular"},
    {"key": "respiratory_rate", "name": "Respiratory Rate", "unit": "breaths/min", "min": 5, "max": 60, "normal_min": 12, "normal_max": 20, "chart_type": "line", "category": "respiratory"},
    {"key": "sleep_duration", "name": "Sleep Duration", "unit": "hours", "min": 0, "max": 24, "normal_min": 7, "normal_max": 9, "chart_type": "bar", "category": "lifestyle"},
    {"key": "physical_activity", "name": "Physical Activity", "unit": "minutes", "min": 0, "max": 1440, "normal_min": 30, "normal_max": 120, "chart_type": "bar", "category": "lifestyle"},
    {"key": "waist_circumference", "name": "Waist Circumference", "unit": "cm", "min": 10, "max": 400, "normal_min": 60, "normal_max": 102, "chart_type": "line", "category": "body"},
    {"key": "weight", "name": "Weight", "unit": "kg", "min": 1, "max": 300, "normal_min": 50, "normal_max": 100, "chart_type": "line", "category": "body"},
    {"key": "hydration", "name": "Hydration Level", "unit": "glasses", "min": 0, "max": 20, "normal_min": 8, "normal_max": 15, "chart_type": "bar", "category": "lifestyle"},
]

VITAL_KEYS = [v["key"] for v in VITAL_TYPES]

PLANS = [
    {"key": "free", "name": "Free", "price": 0, "price_yearly": 0, "currency": "INR", "vital_limit": 2, "chart_history_days": 7, "csv_export": True, "pdf_export": False, "sharing": False, "features": ["Track any 2 vitals of your choice", "7-day chart history", "Basic CSV export", "Basic reminders"]},
    {"key": "standard", "name": "Standard", "price": 299, "price_yearly": 2999, "currency": "INR", "vital_limit": 6, "chart_history_days": 365, "csv_export": True, "pdf_export": True, "sharing": True, "features": ["Track any 6 vitals of your choice", "Full 1-year history", "CSV & PDF export", "Shareable reports", "Advanced reminders", "Better analytics"]},
    {"key": "premium", "name": "Premium", "price": 499, "price_yearly": 4999, "currency": "INR", "vital_limit": 12, "chart_history_days": -1, "csv_export": True, "pdf_export": True, "sharing": True, "features": ["Track all 12 vitals", "Unlimited history", "CSV & PDF export formats", "Full sharing", "Priority support", "Advanced analytics"]},
]

TRANSLATIONS = {
    "en": {
        "app_name": "HealthVitalsTrack", "dashboard": "Dashboard", "daily_tracker": "Daily Tracker",
        "charts_trends": "Charts & Trends", "reports": "Reports", "billing": "Billing",
        "settings": "Settings", "admin_panel": "Admin Panel", "sign_out": "Sign Out",
        "welcome_back": "Welcome back", "active_vitals": "Active Vitals", "todays_entries": "Today's Entries",
        "this_week": "This Week", "plan": "Plan", "health_insights": "Health Insights",
        "quick_actions": "Quick Actions", "your_vitals": "Your Vitals", "log_todays_vitals": "Log Today's Vitals",
        "view_trends": "View Trends", "export_report": "Export Report", "enable_vitals": "Enable Vitals",
        "get_started": "Get Started", "save_all": "Save All", "no_vitals_enabled": "No Vitals Enabled",
        "select_vital": "Select vital", "date_range": "Date Range", "export": "Export",
        "current_plan": "Current Plan", "upgrade": "Upgrade", "downgrade": "Downgrade",
        "switch": "Switch", "profile": "Profile", "manage_vitals": "Manage Vitals",
        "save_profile": "Save Profile", "full_name": "Full Name", "email": "Email",
        "password": "Password", "sign_in": "Sign In", "create_account": "Create Account",
        "dont_have_account": "Don't have an account?", "already_have_account": "Already have an account?",
        "dark_mode": "Dark Mode", "language": "Language", "subscription_billing": "Subscription & Billing",
        "reports_export": "Reports & Export", "shared_reports": "Shared Reports",
        "create_shared_report": "Create Shared Report", "share_link": "Share Link",
        "password_protected": "Password Protected", "expires_in": "Expires in",
        "revoke": "Revoke", "copy_link": "Copy Link", "normal": "Normal", "warning": "Warning",
        "critical": "Critical", "medical_disclaimer": "For informational tracking only. Not a medical device.",
    },
    "hi": {
        "app_name": "HealthVitalsTrack", "dashboard": "डैशबोर्ड", "daily_tracker": "दैनिक ट्रैकर",
        "charts_trends": "चार्ट और रुझान", "reports": "रिपोर्ट", "billing": "बिलिंग",
        "settings": "सेटिंग्स", "admin_panel": "एडमिन पैनल", "sign_out": "साइन आउट",
        "welcome_back": "वापस स्वागत है", "active_vitals": "सक्रिय वाइटल्स", "todays_entries": "आज की एंट्री",
        "this_week": "इस सप्ताह", "plan": "प्लान", "health_insights": "स्वास्थ्य अंतर्दृष्टि",
        "quick_actions": "त्वरित कार्य", "your_vitals": "आपके वाइटल्स", "log_todays_vitals": "आज के वाइटल्स दर्ज करें",
        "view_trends": "रुझान देखें", "export_report": "रिपोर्ट निर्यात करें", "enable_vitals": "वाइटल्स सक्षम करें",
        "get_started": "शुरू करें", "save_all": "सब सेव करें", "no_vitals_enabled": "कोई वाइटल्स सक्षम नहीं",
        "select_vital": "वाइटल चुनें", "date_range": "तारीख सीमा", "export": "निर्यात",
        "current_plan": "वर्तमान प्लान", "upgrade": "अपग्रेड", "downgrade": "डाउनग्रेड",
        "switch": "बदलें", "profile": "प्रोफ़ाइल", "manage_vitals": "वाइटल्स प्रबंधित करें",
        "save_profile": "प्रोफ़ाइल सेव करें", "full_name": "पूरा नाम", "email": "ईमेल",
        "password": "पासवर्ड", "sign_in": "साइन इन", "create_account": "खाता बनाएं",
        "dont_have_account": "खाता नहीं है?", "already_have_account": "पहले से खाता है?",
        "dark_mode": "डार्क मोड", "language": "भाषा", "subscription_billing": "सदस्यता और बिलिंग",
        "reports_export": "रिपोर्ट और निर्यात", "shared_reports": "साझा रिपोर्ट",
        "create_shared_report": "साझा रिपोर्ट बनाएं", "share_link": "लिंक साझा करें",
        "password_protected": "पासवर्ड संरक्षित", "expires_in": "समाप्ति",
        "revoke": "रद्द करें", "copy_link": "लिंक कॉपी करें", "normal": "सामान्य", "warning": "चेतावनी",
        "critical": "गंभीर", "medical_disclaimer": "केवल सूचना ट्रैकिंग के लिए। चिकित्सा उपकरण नहीं है।",
    },
    "te": {
        "app_name": "HealthVitalsTrack", "dashboard": "డాష్‌బోర్డ్", "daily_tracker": "దైనిక ట్రాకర్",
        "charts_trends": "చార్ట్‌లు & ట్రెండ్‌లు", "reports": "రిపోర్ట్‌లు", "billing": "బిల్లింగ్",
        "settings": "సెట్టింగ్‌లు", "admin_panel": "అడ్మిన్ ప్యానెల్", "sign_out": "సైన్ అవుట్",
        "welcome_back": "తిరిగి స్వాగతం", "active_vitals": "యాక్టివ్ వైటల్స్", "todays_entries": "ఈరోజు ఎంట్రీలు",
        "this_week": "ఈ వారం", "plan": "ప్లాన్", "health_insights": "ఆరోగ్య అంతర్దృష్టులు",
        "quick_actions": "త్వరిత చర్యలు", "your_vitals": "మీ వైటల్స్", "log_todays_vitals": "ఈరోజు వైటల్స్ నమోదు చేయండి",
        "view_trends": "ట్రెండ్‌లు చూడండి", "export_report": "రిపోర్ట్ ఎగుమతి చేయండి", "enable_vitals": "వైటల్స్ ఎనేబుల్ చేయండి",
        "get_started": "ప్రారంభించండి", "save_all": "అన్నీ సేవ్ చేయండి", "no_vitals_enabled": "వైటల్స్ ఎనేబుల్ కాలేదు",
        "select_vital": "వైటల్ ఎంచుకోండి", "date_range": "తేదీ పరిధి", "export": "ఎగుమతి",
        "current_plan": "ప్రస్తుత ప్లాన్", "upgrade": "అప్‌గ్రేడ్", "downgrade": "డౌన్‌గ్రేడ్",
        "switch": "మార్చు", "profile": "ప్రొఫైల్", "manage_vitals": "వైటల్స్ నిర్వహించండి",
        "save_profile": "ప్రొఫైల్ సేవ్ చేయండి", "full_name": "పూర్తి పేరు", "email": "ఇమెయిల్",
        "password": "పాస్‌వర్డ్", "sign_in": "సైన్ ఇన్", "create_account": "ఖాతా సృష్టించండి",
        "dont_have_account": "ఖాతా లేదా?", "already_have_account": "ఇప్పటికే ఖాతా ఉందా?",
        "dark_mode": "డార్క్ మోడ్", "language": "భాష", "subscription_billing": "సబ్‌స్క్రిప్షన్ & బిల్లింగ్",
        "reports_export": "రిపోర్ట్‌లు & ఎగుమతి", "shared_reports": "షేర్డ్ రిపోర్ట్‌లు",
        "create_shared_report": "షేర్డ్ రిపోర్ట్ సృష్టించండి", "share_link": "లింక్ షేర్ చేయండి",
        "password_protected": "పాస్‌వర్డ్ రక్షిత", "expires_in": "గడువు",
        "revoke": "రద్దు", "copy_link": "లింక్ కాపీ చేయండి", "normal": "సాధారణ", "warning": "హెచ్చరిక",
        "critical": "తీవ్ర", "medical_disclaimer": "సమాచార ట్రాకింగ్ కోసం మాత్రమే. వైద్య పరికరం కాదు.",
    },
}

CONTENT_PAGES = {
    "terms": {
        "title": "Terms of Service",
        "content": """# Terms of Service\n\n**Last updated: June 2026**

These Terms of Service (“Terms”) govern your access to and use of the VitalTrack website, applications, dashboards, reports, notifications, and related services (collectively, the “Service”) operated by VitalTrack, its affiliates, successors, and authorized service providers (“VitalTrack,” “we,” “us,” or “our”).

By accessing, browsing, registering for, subscribing to, or using the Service, you agree to be bound by these Terms. If you do not agree to these Terms, do not access or use the Service.

## 1. Eligibility and Acceptance

You must be at least 18 years old, or the age of majority in your jurisdiction, to create an account and use the Service on your own behalf. By using the Service, you represent and warrant that you have the legal capacity to enter into a binding agreement.

If you use the Service on behalf of another person, organization, or household member, you represent that you have the authority to do so and to accept these Terms on their behalf.

## 2. Nature of the Service

VitalTrack is a digital health vitals tracking and reporting platform intended for personal organization, wellness monitoring, general informational use, and self-recordkeeping.

The Service may allow you to log, organize, visualize, export, and share information such as blood glucose, blood oxygen, blood pressure, body mass index (BMI), body temperature, heart rate, respiratory rate, sleep duration, physical activity, waist circumference, weight, hydration level, notes, reminders, and related records.

The Service is provided for convenience and informational purposes only. It is not intended to diagnose, treat, cure, prevent, or monitor any disease or medical condition unless explicitly stated otherwise in writing by VitalTrack.

## 3. Medical Disclaimer

VitalTrack is not a medical device, clinical decision-support tool, emergency response system, hospital service, diagnostic platform, or substitute for professional medical advice, diagnosis, or treatment. Medical disclaimers for health-related services should clearly communicate that the service is informational and not professional medical advice. [web:38][web:41][web:44]

You acknowledge and agree that:
- any charts, summaries, trends, alerts, reminders, ranges, educational content, or automated insights made available through the Service are informational only;
- the Service may contain inaccuracies, incomplete entries, user-input errors, synchronization delays, or technical interruptions;
- no output generated by the Service should be relied upon as the sole basis for medical, medication, treatment, emergency, or lifestyle decisions.

Always seek the advice of a qualified physician or other licensed healthcare professional with any questions regarding a medical condition or health concern. Never disregard professional medical advice or delay seeking it because of information provided through the Service.

If you believe you are experiencing a medical emergency, contact local emergency services or a qualified emergency care provider immediately.

## 4. Account Registration and Security

To use some or all parts of the Service, you may be required to create an account. You agree to provide accurate, current, and complete registration information and to keep that information updated.

You are responsible for:
- maintaining the confidentiality of your login credentials;
- all activity occurring under your account;
- promptly notifying us of any suspected unauthorized use, security incident, or account breach.

We may suspend or terminate accounts that contain false information, violate these Terms, present security risks, or are used in a fraudulent, abusive, unlawful, or misleading manner.

## 5. User Content and Health Data Entries

You retain ownership of the information, vitals, notes, uploads, comments, and other content you submit to the Service (“User Content”), subject to the rights you grant to us under these Terms.

By submitting User Content, you grant VitalTrack a non-exclusive, worldwide, revocable, limited license to host, store, process, reproduce, format, transmit, and display that User Content solely to:
- operate and provide the Service;
- generate charts, reports, exports, and reminders;
- support account functionality;
- improve reliability, security, usability, and performance;
- comply with legal obligations and enforce these Terms.

You represent and warrant that:
- you have the necessary rights and permissions to submit the User Content;
- your User Content does not violate any law, third-party right, or contractual obligation;
- your User Content is not knowingly false, misleading, malicious, or harmful.

You are solely responsible for the accuracy, completeness, and legality of your User Content.

## 6. Privacy and Data Handling

Your use of the Service is also subject to our Privacy Policy, which explains how we collect, use, store, share, and protect personal data and health-related information.

Because health-related information may be sensitive, we strive to implement reasonable technical and organizational safeguards appropriate to the nature of the data processed. GDPR-style frameworks emphasize transparency in processing and the use of processors that provide sufficient safeguards. [web:43][web:46]

However, no method of transmission, storage, or processing is completely secure, and we do not guarantee absolute security.

You acknowledge that:
- you choose what information to enter into the Service;
- you are responsible for reviewing what data you upload, record, or share;
- certain features, such as shareable report links, exports, reminders, and email notifications, may increase the exposure risk of your information if used carelessly or on insecure devices.

## 7. Subscription Plans and Paid Features

VitalTrack may offer free and paid plans, including Free, Standard, and Premium tiers, or similarly named subscription plans. Plan names, features, usage limits, billing cycles, pricing, and entitlements may change from time to time.

Paid features may include, depending on the plan:
- additional health vital tracking slots;
- increased history access;
- export features;
- sharable reports;
- premium charts or analytics;
- advanced reminders and scheduling;
- priority support;
- future integrations or mobile app capabilities.

We may provide details of current plans, pricing, renewal terms, and included features on our pricing page or in-app billing area.

## 8. Billing, Renewals, and Payment Processing

If you purchase a paid plan, you authorize VitalTrack and its third-party payment processors to charge the applicable fees, taxes, levies, and recurring subscription amounts using your selected payment method.

Payments may be processed through third-party providers such as Razorpay, PayU, Stripe, or other processors designated by us. Subscription cancellation is generally controlled by the business providing the service, not by Stripe acting on the business’s behalf. [web:39]

By making a purchase, you agree that:
- all billing information you provide is accurate and complete;
- recurring subscriptions may renew automatically unless canceled in accordance with the applicable billing settings;
- we may suspend or limit paid features if payment cannot be collected, is reversed, is disputed, or is flagged as fraudulent.

Where applicable:
- taxes, GST, VAT, or similar charges may be added;
- prices may be displayed in INR or another supported currency;
- invoices or payment confirmations may be issued electronically.

You are responsible for reviewing your plan terms, renewal date, and cancellation status from your account or billing communications.

## 9. Cancellations, Downgrades, and Refunds

You may cancel your paid subscription at any time through your account settings or by contacting support, subject to any minimum billing commitment, promotional term, or country-specific law.

Unless otherwise stated:
- cancellation will typically take effect at the end of the current paid billing period;
- downgrading may reduce access to certain features immediately or at the next billing cycle;
- historical records may remain stored but some features or views may become unavailable under lower-tier plans;
- unused portions of a billing period may be non-refundable except where required by law or where we expressly agree otherwise.

Refund requests are reviewed in accordance with our posted refund policy, applicable law, and payment processor constraints. Some payment processor operations, including refunds, may be subject to operational and banking timing limits. [web:45]

We reserve the right to deny refund requests in cases including abuse, repeated refund claims, misuse of trials, policy violations, or circumstances where the Service has already been substantially delivered, except where prohibited by law.

## 10. Free Plans, Trials, and Promotional Offers

We may offer free plans, trial periods, introductory discounts, coupons, credits, referral benefits, or promotional access. Such offers may be limited by time, geography, eligibility, account history, or method of payment.

We may modify or withdraw promotional offers at any time, subject to applicable law. If a trial converts into a paid subscription, you are responsible for canceling before the conversion date if you do not wish to be charged.

## 11. Acceptable Use

You agree not to, and not to assist or permit others to:
- use the Service for unlawful, fraudulent, deceptive, abusive, defamatory, or harmful purposes;
- upload malicious code, viruses, bots, or scripts;
- interfere with the security, integrity, availability, or proper functioning of the Service;
- attempt unauthorized access to accounts, infrastructure, data, APIs, or administrative systems;
- scrape, harvest, reverse engineer, reproduce, frame, resell, or exploit the Service except as expressly permitted;
- use the Service to impersonate another person or misrepresent affiliation;
- submit content that infringes intellectual property, privacy, publicity, confidentiality, or other legal rights;
- use automated means to access the Service in a way that imposes unreasonable load or bypasses controls;
- use the Service in violation of medical advertising, consumer protection, privacy, or data protection laws.

We may investigate, suspend, restrict, or terminate access for actual or suspected violations.

## 12. Reports, Exports, and Sharing Features

The Service may allow you to generate PDF or CSV reports, dashboards, summaries, visualizations, and secure shareable links.

You are solely responsible for:
- choosing what information to include in exported or shared reports;
- maintaining the confidentiality of links, passwords, downloaded files, and recipient access;
- ensuring that you have authorization to share any information about another person.

We do not control how recipients use information once you export or share it outside the Service. If you enable a shareable link, anyone with access to that link and any associated credentials may be able to view the shared data until the link expires or is revoked.

## 13. Notifications and Communications

By using the Service, you consent to receive service-related communications such as account notices, billing alerts, security updates, password resets, support responses, and transactional emails.

Where enabled by your settings or permitted by law, you may also receive:
- reminder emails or notifications;
- missed-entry alerts;
- weekly or periodic summaries;
- product updates and educational content.

You may be able to opt out of certain non-essential communications, but you may not opt out of transactional or legally required notices necessary to operate your account or comply with law.

## 14. Third-Party Services and Integrations

The Service may integrate with or rely on third-party providers for payments, email delivery, cloud hosting, analytics, notifications, support tools, maps, embedded content, identity verification, or future wearable/device integrations.

We are not responsible for the acts, omissions, availability, content, policies, or security practices of third-party services. Your use of third-party services may be subject to separate terms and privacy policies.

## 15. Intellectual Property

The Service, including its software, design, text, graphics, logos, trademarks, service marks, interfaces, compilations, and non-user-generated content, is owned by or licensed to VitalTrack and is protected by applicable intellectual property laws.

Except as expressly permitted by these Terms, you may not copy, modify, distribute, sell, sublicense, reverse engineer, decompile, create derivative works from, or otherwise exploit any part of the Service.

VitalTrack and related names, logos, and branding elements are protected marks and may not be used without prior written permission.

## 16. Feedback

If you submit feedback, suggestions, ideas, improvement requests, or feature recommendations, you grant us a non-exclusive, worldwide, perpetual, irrevocable, royalty-free license to use, reproduce, adapt, modify, publish, and incorporate that feedback without restriction or compensation to you.

## 17. Availability and Changes to the Service

We may update, modify, suspend, discontinue, or restrict any aspect of the Service, including features, plans, interfaces, APIs, and availability, at any time, with or without notice, except where notice is required by law.

We do not guarantee that the Service will be uninterrupted, error-free, secure, or available at all times. Scheduled maintenance, emergency maintenance, outages, provider failures, and connectivity issues may affect availability.

We may release beta, preview, experimental, or limited features, which are provided “as is” and may be modified or discontinued without liability.

## 18. Disclaimers of Warranties

To the fullest extent permitted by applicable law, the Service is provided on an “as is” and “as available” basis, without warranties of any kind, whether express, implied, statutory, or otherwise.

Without limiting the foregoing, VitalTrack disclaims all warranties relating to:
- merchantability;
- fitness for a particular purpose;
- non-infringement;
- accuracy, reliability, completeness, or timeliness of content;
- uninterrupted availability;
- data preservation;
- compatibility with every device, browser, network, or operating system;
- medical usefulness or clinical suitability.

We do not warrant that:
- the Service will meet your needs or expectations;
- any trend, reminder, summary, threshold, or export will be accurate or complete;
- defects will be corrected;
- the Service is free of harmful components;
- any data will never be lost, corrupted, delayed, or inaccessible.

## 19. Limitation of Liability

To the maximum extent permitted by law, VitalTrack and its affiliates, officers, directors, employees, contractors, licensors, vendors, and service providers shall not be liable for any indirect, incidental, consequential, special, exemplary, punitive, or speculative damages, including damages for loss of profits, data, goodwill, business interruption, health outcomes, or procurement of substitute services, arising out of or related to the Service or these Terms.

To the fullest extent permitted by law, our aggregate liability for any claim arising from or relating to the Service shall not exceed the greater of:
- the amount you paid to VitalTrack for the Service in the 12 months preceding the event giving rise to the claim; or
- the minimum amount required by applicable law.

Nothing in these Terms excludes liability that cannot be excluded under applicable law.

## 20. Indemnification

You agree to defend, indemnify, and hold harmless VitalTrack and its affiliates, personnel, contractors, licensors, and service providers from and against any claims, actions, proceedings, liabilities, damages, losses, costs, and expenses, including reasonable legal fees, arising out of or related to:
- your use or misuse of the Service;
- your User Content;
- your violation of these Terms;
- your violation of any law, regulation, or third-party right;
- your sharing of data without proper authority or consent.

## 21. Suspension and Termination

We may suspend, restrict, or terminate your access to the Service, with or without notice, if:
- you violate these Terms;
- you fail to pay applicable fees;
- your account presents a security, legal, or fraud risk;
- required by law, court order, regulator, or payment provider;
- continuing to provide the Service to you becomes commercially or technically impracticable.

You may stop using the Service at any time. Termination does not relieve you of obligations accrued before termination, including payment obligations.

Sections that by their nature should survive termination will survive, including provisions relating to payment, intellectual property, disclaimers, limitations of liability, indemnity, dispute resolution, and data handling where applicable.

## 22. Data Retention and Deletion

We may retain account information, transactional records, backups, logs, support records, and legally required information for as long as reasonably necessary to operate the Service, comply with law, resolve disputes, prevent fraud, and enforce our agreements.

Deletion requests may be subject to identity verification, technical constraints, backup retention cycles, fraud-prevention requirements, accounting obligations, and legal retention duties.

Where required by law, we will provide mechanisms to access, export, correct, or delete eligible personal data.

## 23. International Use

The Service may be accessed from multiple countries. You are responsible for ensuring that your use of the Service complies with local laws applicable to you.

If you access the Service from a jurisdiction with specific health, privacy, consumer, or electronic contracting requirements, you acknowledge that additional legal rights or obligations may apply.

## 24. Governing Law and Dispute Resolution

These Terms shall be governed by and construed in accordance with the laws applicable in the jurisdiction where VitalTrack is established, unless otherwise required by mandatory consumer protection laws.

Any dispute, controversy, or claim arising out of or relating to these Terms or the Service shall first be attempted to be resolved through good-faith discussions by contacting support.

If informal resolution fails, disputes shall be submitted to the courts or dispute resolution forum specified in VitalTrack’s legal notices, subject to any mandatory rights you may have under applicable law.

If you operate in multiple jurisdictions, include a jurisdiction-specific governing law and venue clause before publishing this document.

## 25. Changes to These Terms

We may revise these Terms from time to time to reflect changes in the Service, laws, regulations, payment methods, business practices, or risk controls.

When required, we will provide notice by posting the updated Terms on the website, updating the “Last updated” date, sending email notice, or providing an in-app notification. Continued use of the Service after the effective date of updated Terms constitutes acceptance of the revised Terms, except where additional consent is required by law.

## 26. Severability and Waiver

If any provision of these Terms is held to be invalid, illegal, or unenforceable, the remaining provisions shall remain in full force and effect.

Our failure to enforce any provision of these Terms shall not constitute a waiver of that provision or any other right.

## 27. Entire Agreement

These Terms, together with our Privacy Policy, Refund Policy, and any additional plan-specific or feature-specific terms presented to you, constitute the entire agreement between you and VitalTrack regarding the Service and supersede prior or contemporaneous understandings relating to the Service.

## 28. Contact Information

If you have questions about these Terms, billing, cancellations, data requests, or legal notices, please contact:

**VitalTrack Support**  
Email: mail@altty.com  
Website: https://www.vitaltrack.in  
Support Hours: 9 AM to 6 PM (IST)  
Registered Address: AaVi Technos, 150/2RT, Vijaya Nagar Colony, Hyderabad, INDIA - 500057"""
    },
    "privacy": {
        "title": "Privacy Policy",
        "content": """# Privacy Policy\n\n**Last updated: June 2026**

VitalTrack (“VitalTrack,” “we,” “us,” or “our”) respects your privacy and is committed to protecting your personal data. This Privacy Policy explains how we collect, use, store, disclose, protect, and otherwise process your information when you access or use the VitalTrack website, applications, dashboards, reports, notifications, and related services (collectively, the “Service”).

This Privacy Policy is intended to provide clear, transparent information about our data practices. Health and wellness apps should clearly disclose what data they collect, why they collect it, who receives it, and what controls users have, and privacy-by-design and data minimization are widely recommended for apps that process health-related information. [web:58][web:59][web:61][web:63][web:66]

By using the Service, creating an account, subscribing to a plan, entering health information, or otherwise interacting with us, you acknowledge that you have read and understood this Privacy Policy.

## 1. Scope of This Privacy Policy

This Privacy Policy applies to:
- our website and web application;
- user dashboards and account areas;
- email, reminder, and support communications;
- exported reports and sharable report features;
- future mobile app experiences, if and when launched;
- any related products, pages, forms, or interactions that link to this Privacy Policy.

This Privacy Policy does not apply to third-party websites, payment gateways, email providers, analytics tools, or services that operate under their own privacy policies.

## 2. Important Notice About Health-Related Data

The Service may process information that relates to your health, wellness, body measurements, or daily vital records. Depending on the laws applicable to you, some of this information may be considered sensitive personal data or a special category of personal data. GDPR-oriented guidance treats health data as a sensitive category and emphasizes clear disclosure, lawful basis, storage periods, rights, recipients, and security measures. [web:59][web:62]

We encourage you to use discretion when entering information into the Service and to avoid uploading unnecessary or excessive personal data.

We design our Service with the goal of minimizing unnecessary data collection and supporting user control over what is stored, exported, or shared. Privacy-by-design and data minimization are widely recommended for health apps handling personal health information. [web:58][web:61][web:63]

## 3. Information We Collect

We may collect the following categories of information:

### 3.1 Account and Identity Information
- full name;
- email address;
- phone number, if provided;
- login credentials or authentication details;
- account preferences;
- profile information such as age, gender, height, language, timezone, and measurement preferences.

### 3.2 Health and Wellness Information
You may choose to enter and store health-related or wellness-related information such as:
- blood glucose level;
- blood oxygen level;
- blood pressure;
- body mass index (BMI);
- body temperature;
- heart rate (pulse);
- respiratory rate;
- sleep duration;
- physical activity;
- waist circumference;
- weight;
- hydration level;
- notes, tags, comments, and related observations;
- reminder settings and tracking preferences.

### 3.3 Billing and Subscription Information
If you subscribe to a paid plan, we may collect or receive:
- subscription plan selection;
- billing status;
- invoice and transaction references;
- payment history and renewal status;
- limited payment-related information from third-party processors.

We generally do not store full card numbers or full payment instrument details when payments are handled by external gateways.

### 3.4 Device, Technical, and Usage Information
We may automatically collect:
- IP address;
- browser type and version;
- operating system;
- device identifiers;
- language and locale settings;
- session activity;
- pages visited;
- feature usage;
- timestamps;
- referral URLs;
- crash or performance logs;
- cookies and similar technologies where applicable.

### 3.5 Communications and Support Data
When you contact us or interact with support, we may collect:
- support requests;
- feedback and survey responses;
- chat or email content;
- screenshots or attachments you provide;
- records of account issues, complaints, or service requests.

### 3.6 Shared and Exported Content
If you create exports or share reports, we may process:
- report generation metadata;
- selected date ranges and vital categories;
- file generation history;
- sharable link creation, expiration, and revocation data;
- download or access logs where technically available.

## 4. How We Collect Information

We collect information:
- directly from you when you register, subscribe, enter vitals, upload content, configure reminders, generate reports, or contact support;
- automatically through your use of the Service and your device/browser interactions;
- from third-party providers such as payment processors, email services, analytics providers, or authentication providers;
- from cookies, local identifiers, or similar technologies where lawfully used and disclosed.

Health app privacy guidance emphasizes providing clear and accessible notice before users submit health data and explaining the reasons for processing and any disclosures to third parties. [web:61][web:66]

## 5. Why We Process Your Information

We may process your information for the following purposes:

### 5.1 To Provide and Operate the Service
- create and manage accounts;
- authenticate users;
- store and display health tracking entries;
- generate charts, dashboards, reports, and summaries;
- support subscription entitlements and plan limits;
- enable sharing and export features.

### 5.2 To Communicate With You
- send verification emails;
- deliver password reset emails;
- send billing and payment notices;
- send reminders, alerts, and summaries based on your settings;
- respond to support requests and service inquiries.

### 5.3 To Improve the Service
- understand user behavior and product usage;
- improve performance, reliability, accessibility, and design;
- identify bugs, abuse, errors, and service issues;
- test new features and optimize workflows.

### 5.4 To Secure the Service
- detect fraud, abuse, and unauthorized access;
- enforce our Terms and internal policies;
- audit access and maintain logs;
- investigate incidents and respond to potential security threats.

### 5.5 To Comply With Legal and Regulatory Obligations
- maintain accounting and tax records;
- respond to lawful requests or legal process;
- enforce legal rights and contractual obligations;
- comply with applicable data protection, consumer protection, and financial rules.

### 5.6 To Support Business Operations
- maintain backups;
- administer plans and pricing;
- manage service providers;
- perform internal analytics on a de-identified or aggregated basis where feasible.

GDPR-oriented transparency guidance states that users should be told who is processing their data, why it is being processed, what legal basis applies, who receives it, how long it is stored, and what rights they have. [web:59]

## 6. Legal Bases for Processing

Where required by applicable law, we rely on one or more of the following legal bases for processing:
- your consent;
- performance of a contract or steps requested by you before entering into a contract;
- compliance with legal obligations;
- our legitimate interests, where those interests are not overridden by your rights and interests;
- protection against fraud, security risks, or misuse.

If we rely on consent for certain processing activities, you may withdraw that consent where permitted by law, but withdrawal will not affect processing already lawfully carried out before withdrawal. GDPR guidance emphasizes documenting and communicating the lawful basis and explaining how consent may be withdrawn where consent is used. [web:59][web:62]

## 7. Cookies and Similar Technologies

We may use cookies, pixels, local storage equivalents, session tokens, analytics tools, and similar technologies to:
- keep you signed in;
- remember settings and preferences;
- improve site performance;
- analyze traffic and product usage;
- enhance security;
- support basic functionality.

Depending on your jurisdiction, we may request consent for non-essential cookies or provide cookie controls through a consent banner or preference center.

You can also manage cookies through your browser settings, although disabling certain technologies may affect Service functionality.

## 8. How We Share Information

We do not sell your personal data in the ordinary sense of selling customer lists for cash. AMA privacy guidance for health apps emphasizes giving individuals control over sharing and preventing unconsented access by employers and insurers. [web:58]

We may share information in the following circumstances:

### 8.1 Service Providers and Processors
We may share information with trusted vendors who help us operate the Service, such as:
- cloud hosting providers;
- database and storage providers;
- analytics providers;
- email delivery and notification vendors;
- payment processors;
- customer support tools;
- security and monitoring providers.

Where required, we expect processors to provide sufficient safeguards and process data under appropriate contractual restrictions. GDPR guidance specifically requires controllers to use processors that provide sufficient guarantees and appropriate technical and organizational measures. [web:43][web:59]

### 8.2 Payment Providers
We may share payment-related information with processors such as Razorpay, PayU, Stripe, banks, or fraud-prevention partners to process payments, handle subscriptions, prevent abuse, and maintain billing records.

### 8.3 Sharing at Your Direction
We may share information when you:
- generate a public or restricted report link;
- send a report to a third party;
- authorize an integration;
- request support actions involving your account data.

### 8.4 Legal and Compliance Reasons
We may disclose information when we believe disclosure is necessary to:
- comply with law, regulation, subpoena, court order, or lawful government request;
- protect rights, property, or safety;
- investigate fraud, abuse, or security incidents;
- enforce our Terms or other agreements.

### 8.5 Business Transfers
If we undergo a merger, acquisition, financing, reorganization, sale of assets, or similar transaction, your information may be disclosed as part of that process, subject to applicable confidentiality and legal protections.

### 8.6 Aggregated or De-Identified Information
We may use or disclose aggregated, anonymized, or de-identified information for analytics, benchmarking, service improvement, reporting, or business planning, provided that it does not reasonably identify you.

## 9. Data Retention

We retain personal data only for as long as reasonably necessary for the purposes described in this Privacy Policy, unless a longer retention period is required or permitted by law. GDPR guidance recommends clearly stating storage periods or the criteria used to determine them. [web:59]

Retention periods may depend on:
- account status;
- subscription and billing records;
- legal, tax, accounting, and audit requirements;
- support history;
- fraud-prevention needs;
- backup cycles and system recovery periods;
- unresolved disputes or claims.

Examples:
- account information may be retained while your account remains active;
- billing and tax records may be retained for legally required periods;
- backup copies may persist temporarily after deletion requests;
- audit logs may be retained to support security and compliance obligations.

When data is no longer needed, we aim to delete, anonymize, or securely isolate it, subject to technical and legal constraints.

## 10. Data Security

We use reasonable technical, administrative, and organizational measures designed to protect your personal data. Health privacy guidance emphasizes strong security, minimum necessary collection, and protection against unauthorized access and disclosure. [web:58][web:60][web:66]

These measures may include:
- HTTPS/TLS encryption in transit;
- access controls and role restrictions;
- password hashing;
- secure infrastructure configuration;
- audit logging;
- monitoring and alerting;
- backup and recovery controls;
- environment segregation;
- tokenized or limited handling of payment data;
- signed URLs or protected report access;
- least-privilege access practices.

However, no system can guarantee absolute security. You are also responsible for protecting your password, device access, and any exported or shared copies of your data.

## 11. International Data Transfers

Depending on where you access the Service from and where our vendors operate, your information may be processed in countries other than your own. When required, we will use appropriate safeguards for international transfers as required by applicable law. GDPR transparency guidance states that users should be informed of international transfers and the measures applied where relevant. [web:59]

## 12. Your Privacy Rights

Depending on your location and applicable law, you may have rights such as:
- the right to know whether we process your personal data;
- the right to access your personal data;
- the right to receive a copy of your data in an accessible format;
- the right to correct inaccurate information;
- the right to request deletion of eligible data;
- the right to object to or restrict certain processing;
- the right to withdraw consent where consent is the basis;
- the right to data portability where applicable;
- the right to complain to a regulator or data protection authority.

GDPR guidance specifically highlights rights of access, correction, erasure, restriction, objection, portability, and withdrawal of consent where consent is the legal basis. [web:59][web:62]

We may need to verify your identity before processing certain requests. Some rights may be limited by law, security obligations, contractual requirements, technical feasibility, or overriding legitimate grounds.

## 13. Account Controls and User Choices

You may be able to:
- update account and profile details;
- change language and notification settings;
- edit or delete certain vital records;
- disable sharable links;
- cancel subscriptions;
- request export of your account data;
- request deletion of your account subject to applicable conditions;
- opt out of non-essential emails where available.

Health privacy guidance emphasizes configurable user controls and granular sharing preferences for personal health information. [web:58]

## 14. Children’s Privacy

The Service is generally intended for adults and is not directed to children under the age specified in our Terms or under applicable law without proper authorization. We do not knowingly collect personal data from children in violation of applicable law.

If you believe a child has provided personal information to us without proper consent, please contact us so we can review and take appropriate action.

## 15. Automated Processing and Analytics

We may use automated systems to:
- generate trend summaries;
- highlight missed entries;
- provide reminders;
- classify usage patterns;
- detect suspicious activity or abuse;
- produce internal analytics.

These functions are intended to support the operation and usability of the Service. They are not intended to provide clinical diagnosis, treatment recommendations, or emergency decisions.

Where required by law, we will provide additional information about automated decision-making and its significance. GDPR transparency guidance states that, where applicable, users should be told about automated decision-making, its logic, and its consequences. [web:59]

## 16. Report Sharing, Exports, and User Responsibility

The Service may allow you to export reports in formats such as PDF or CSV and to create sharable links.

Please note:
- exported files may leave the protected environment of the Service;
- anyone you share a file or link with may copy, retain, or further share that information;
- your privacy may be affected if you use shared devices, insecure email, or public links;
- you are responsible for deciding what data to share and with whom.

We encourage users to share only the minimum information necessary for the intended purpose. Privacy-by-design principles recommend limiting disclosure to only the data needed for the immediate and specific purpose. [web:63]

## 17. Data Breach and Security Incident Response

We take security incidents seriously and maintain processes intended to identify, investigate, contain, and respond to suspected incidents. FTC health privacy materials highlight the importance of strong privacy and security practices and note that certain health apps may face breach-related obligations. [web:47][web:60][web:65][web:66]

Where required by applicable law, we may notify affected individuals, regulators, partners, or authorities regarding certain confirmed breaches or incidents involving personal data.

## 18. Third-Party Links and Services

Our Service may contain links to third-party websites, resources, embedded services, or payment pages. We are not responsible for the privacy, security, content, or data practices of those third parties. We encourage you to review their privacy policies before providing information.

## 19. Do Not Track and Similar Signals

Some browsers or devices may send “Do Not Track” or similar signals. Because there is not always a consistent industry standard for responding to such signals, our response may vary depending on the technology and jurisdiction involved.

## 20. Changes to This Privacy Policy

We may update this Privacy Policy from time to time to reflect changes in our practices, features, legal obligations, technologies, or business operations.

When required, we will provide notice by:
- updating the “Last updated” date;
- posting the revised Privacy Policy on the website or in the app;
- sending an email;
- displaying an in-app notice;
- requesting renewed consent where legally required.

Your continued use of the Service after an update becomes effective means you acknowledge the revised Privacy Policy, unless additional consent is required by law.

## 21. Contact Us

If you have questions, concerns, requests, or complaints about this Privacy Policy or our data practices, please contact us at:

**VitalTrack Privacy Team**  
Email: mail@altty.com  
Support Email: mail@altty.com  
Website: https://www.vitaltrack.in  
Registered Address: AaVi Technos, 150/2RT, Vijaya Nagar Colony, Hyderabad, INDIA - 500057
Data Protection Contact / Grievance Officer: Mohan Valluri

If you are located in a jurisdiction that grants you specific privacy rights, you may also have the right to contact your local data protection or consumer protection authority."""
    },
    "refund": {
        "title": "Refund & Cancellation Policy",
        "content": """# Refund & Cancellation Policy\n\n**Last updated: June 2026**

This Refund & Cancellation Policy (“Policy”) explains how cancellations, subscription changes, payment disputes, failed transactions, refunds, renewals, and related billing matters are handled for the VitalTrack website, application, dashboard, and associated services (collectively, the “Service”).

This Policy should be read together with our Terms of Service and Privacy Policy. Payment providers such as Razorpay and Stripe generally require customers to contact the merchant directly for cancellation and refund requests, and PayU recommends merchants publish a clear refund policy including timelines and process details on their website. [web:67][web:39][web:70]

By purchasing, subscribing to, renewing, upgrading, downgrading, or otherwise paying for the Service, you agree to this Policy.

## 1. Scope of This Policy

This Policy applies to:
- free-to-paid upgrades;
- Standard and Premium subscription purchases;
- monthly and annual subscriptions;
- renewals and recurring billing;
- manual and automatic cancellations;
- full and partial refund requests where applicable;
- failed or duplicate payment situations;
- subscription downgrades;
- payment disputes and chargebacks;
- purchases processed through supported gateways such as Razorpay, PayU, and Stripe.

This Policy does not override any non-waivable rights that may apply to you under consumer protection or payment laws in your jurisdiction.

## 2. General Billing Principles

VitalTrack is a subscription-based digital service. Access to paid features is generally granted immediately or shortly after successful payment confirmation.

Because digital subscription access may begin as soon as a plan is activated, not all payments are automatically refundable. Whether a refund is granted may depend on factors such as:
- whether access was activated;
- whether the request concerns the first purchase or a renewal;
- whether the issue was caused by duplicate billing, technical failure, or unauthorized payment;
- whether benefits under the plan were materially used;
- whether law requires a refund in your jurisdiction.

Payment gateways usually act as payment facilitators, while the merchant determines the service-specific cancellation and refund rules; Razorpay and Stripe both direct customers to the business for such requests, and PayU provides merchant-side mechanisms for initiating full or partial refunds. [web:67][web:39][web:68][web:70]

## 3. Subscription Plans Covered by This Policy

This Policy applies to the following plan types, if offered:
- Free Plan;
- Standard Plan;
- Premium Plan;
- monthly subscriptions;
- annual subscriptions;
- promotional or discounted plans;
- trial conversions, if trials are offered;
- custom enterprise or institutional plans, if separately contracted.

Any custom contract, enterprise agreement, reseller agreement, or partner arrangement may include separate billing or refund terms. In the event of conflict, the signed custom agreement will govern to the extent permitted by law.

## 4. Cancellation by the User

You may cancel your paid subscription at any time from your account billing settings or by contacting our support team through the designated support channels.

When you cancel:
- your subscription will typically remain active until the end of the current paid billing cycle, unless otherwise stated;
- future renewals should stop after cancellation is successfully processed;
- you will generally not be charged for the next billing period once cancellation is effective;
- previously paid fees are generally non-refundable except where this Policy or applicable law provides otherwise.

For recurring subscriptions handled by third-party billing processors, cancellation generally needs to be processed through the merchant service and its subscription controls, because payment platforms such as Stripe do not cancel subscriptions on behalf of end customers and direct users to contact the business. [web:39]

You are responsible for canceling before the next renewal date if you do not want your subscription to renew.

## 5. Cancellation Effective Date

The effective date of cancellation will usually be:
- the date you successfully cancel within your account; or
- the date our support team confirms cancellation if manual intervention is required.

If a cancellation request is submitted very close to an upcoming renewal, the renewal may still process if the cancellation cannot be completed before the billing cut-off. In such cases, you should contact support promptly so the matter can be reviewed based on timing, system logs, and applicable law.

## 6. No Retroactive Cancellation Rule

Unless required by law or expressly approved by VitalTrack, subscription cancellations are generally prospective, not retroactive. This means:
- canceling stops future billing;
- canceling does not automatically reverse a previously completed charge;
- access may continue until the end of the paid period.

## 7. Free Trial Cancellation, If Offered

If VitalTrack offers a free trial:
- you may cancel any time during the trial period to avoid conversion into a paid subscription;
- once the free trial converts into a paid plan, standard paid billing terms will apply;
- failure to cancel before trial expiry may result in automatic billing if you previously authorized recurring payment.

We recommend canceling well before the trial end date to avoid unintended renewal due to timing, banking delays, or processing cutoffs.

## 8. Upgrade Policy

If you upgrade from a lower-tier plan to a higher-tier plan:
- the upgrade may take effect immediately or at the next billing cycle, depending on configuration;
- billing may be prorated where technically supported;
- newly unlocked features may become available immediately upon successful payment or billing adjustment;
- prior plan payments are generally not refunded solely because you chose to upgrade.

If proration is supported through the billing system, the adjustment may be handled through the gateway or our internal subscription logic. Stripe supports subscription lifecycle and proration-related billing workflows, and merchant systems commonly normalize those changes in their own billing records. [web:74][web:71]

## 9. Downgrade Policy

If you downgrade from Premium to Standard or from Standard to Free:
- the downgrade may take effect immediately or at the end of the current billing cycle, depending on product settings;
- access to premium features may remain available until the end of the active paid period if your plan is set to expire naturally;
- if the downgrade results in plan restrictions, some vitals or features may become read-only;
- historical data may remain stored but access may be limited under the lower-tier plan;
- downgrade requests do not automatically entitle you to a refund for the unused portion of the current cycle unless required by law or expressly stated otherwise.

If a prorated credit is issued internally, it may be applied as service credit, invoice credit, or partial refund where operationally feasible and legally appropriate.

## 10. Renewal Policy

Paid subscriptions may renew automatically at the end of each billing cycle unless canceled before renewal.

By purchasing a recurring plan, you authorize recurring charges using your selected payment method and gateway, subject to the payment processor’s rules and your bank or issuer’s authorization process.

Renewal timing may depend on:
- billing cycle date;
- payment gateway processing;
- bank authorization success;
- mandate validity for recurring payments;
- tax calculations;
- temporary retry logic after failed charges.

It is your responsibility to:
- maintain a valid payment method;
- monitor upcoming renewals;
- cancel in time if you do not wish to continue.

Razorpay publishes recurring payment cancellation guidance for end users and merchants, and auto-debit flows can depend on the bank, mandate setup, and recurring payment configuration. [web:72]

## 11. Refund Eligibility Overview

Refunds may be considered on a case-by-case basis. A refund is more likely to be considered in situations such as:
- duplicate payment;
- multiple charges for the same subscription period;
- technical failure where payment succeeded but paid access was not provisioned within a reasonable time;
- erroneous billing caused by our system;
- unauthorized transaction subject to verification;
- cancellation requested under mandatory legal rights;
- failure to deliver a purchased service feature due to our confirmed fault.

Refunds are less likely or may be denied where:
- the subscription was knowingly purchased and substantially used;
- the request relates only to non-use or change of mind after meaningful access was already provided;
- the user forgot to cancel before renewal;
- the issue arises from device incompatibility, internet issues, or third-party conditions outside our control after reasonable access was made available;
- the request is abusive, fraudulent, or inconsistent with system records.

## 12. Non-Refundable Situations

Unless required by law, the following are generally non-refundable:
- partially used billing periods;
- unused time remaining in an active subscription after voluntary cancellation;
- failure to use the Service after purchase;
- dissatisfaction based solely on personal preference where the Service was delivered substantially as described;
- missed cancellation before auto-renewal;
- charges resulting from failure to remove or update a valid payment method;
- charges incurred after account sharing or credential compromise caused by your failure to secure your login;
- delays caused solely by banking systems after a refund has already been properly initiated.

## 13. Duplicate, Failed, and Erroneous Transactions

### 13.1 Duplicate Charges
If you believe you were charged more than once for the same transaction, contact us with:
- your registered email address;
- transaction ID;
- payment date;
- payment amount;
- screenshot or bank reference, if available.

If we confirm a duplicate charge, we may issue a full or partial refund as appropriate.

### 13.2 Failed but Debited Transactions
Sometimes a payment may appear debited at the bank level while service activation fails temporarily. In such cases:
- activation may complete after delayed confirmation; or
- the payment may be automatically reversed by banking systems; or
- a manual review may be required.

PayU recommends publishing merchant refund handling and timeline details, and its documentation notes refunds may be initiated to the original source account and can take approximately 5 to 21 days to reflect, depending on the payment method and banking network. [web:70][web:73]

### 13.3 Unauthorized Transactions
If you believe a transaction was unauthorized:
- contact us immediately;
- secure your account credentials;
- notify your payment provider or bank where appropriate;
- provide relevant transaction details.

We may investigate such cases using account logs, device activity, billing metadata, and internal fraud controls before determining next steps.

## 14. Partial Refunds

In limited cases, we may provide partial refunds, credits, or billing adjustments, such as:
- partial service outage impacting paid features materially;
- billing overlap during subscription migration;
- duplicate feature charges;
- approved goodwill resolution;
- legally required partial adjustment.

PayU supports both full and partial refunds through merchant workflows, and merchant dashboards can typically track refund status after initiation. [web:68][web:70]

## 15. Full Refunds

A full refund may be considered in circumstances such as:
- confirmed duplicate full payment;
- accidental multiple subscription purchases for the same account and same service period;
- payment collected but service not provisioned due to our verified technical failure;
- legally mandated cancellation/refund rights;
- exceptional cases approved by VitalTrack support or billing operations.

Approval of a full refund does not obligate us to grant future refunds in similar circumstances if the factual situation differs.

## 16. Refund Request Procedure

To request a refund, please contact us through the official support email or billing support channel and include:
- your full name;
- registered email address;
- subscription plan;
- transaction ID or invoice number;
- payment date;
- payment amount;
- payment gateway used, if known;
- clear reason for the request;
- screenshots or supporting records, if available.

We may request additional information necessary to verify identity, account ownership, billing records, or the basis of the request.

Submitting a refund request does not guarantee approval.

## 17. Refund Review Timeline

We aim to review refund requests within a commercially reasonable time. Review times may vary depending on:
- completeness of the information provided;
- payment gateway logs;
- fraud checks;
- volume of requests;
- whether additional bank confirmation is needed;
- legal or compliance review needs.

If approved, the refund will be initiated through the original payment channel where possible.

## 18. Refund Method and Processing Time

Approved refunds are generally sent back to the original payment source, subject to gateway and banking limitations.

Actual credit timelines are often outside the merchant’s direct control after refund initiation. Razorpay notes that customers should route cancellation queries to the merchant and that, once a refund is initiated, the amount may generally be credited in around 5 to 7 business days in many cases, while PayU documentation states refunds can take roughly 5 to 21 days depending on the payment method and the bank involved. [web:67][web:70]

Estimated refund timelines may vary by:
- credit card;
- debit card;
- UPI;
- net banking;
- wallet;
- EMI or lender-based payment methods;
- international card rails.

A refund is considered initiated when it has been properly submitted to the relevant payment system, not necessarily when the amount appears in your bank account.

## 19. Gateway-Specific Notes

### 19.1 Razorpay
Razorpay acts as a payment facilitator and directs customers to contact the merchant regarding cancellation and refund matters; after a refund is initiated, settlement back to the source may still take several business days depending on the bank and payment method. [web:67]

### 19.2 PayU
PayU provides merchant workflows for full and partial refunds and recommends that merchants clearly publish refund processes and timelines; its documentation explains that refunds are generally returned to the original source account and may take approximately 5 to 21 days to reflect. [web:68][web:70][web:73]

### 19.3 Stripe
Stripe’s support guidance for end customers states that customers generally need to contact the business directly for subscription cancellation or refund issues, because Stripe is not authorized to cancel subscriptions on behalf of the merchant’s customers. [web:39]

## 20. Chargebacks and Payment Disputes

If you initiate a chargeback, dispute, reversal, or similar claim through your bank or payment provider:
- we may suspend or restrict access to the related paid account while the matter is under review;
- we may provide relevant records to the payment processor, acquiring bank, or dispute program;
- we may contest chargebacks that we believe are invalid, abusive, or inconsistent with our records.

Before opening a chargeback, we strongly encourage you to contact us so we can attempt to resolve the issue directly.

## 21. Cancellation or Refund by VitalTrack

We reserve the right to cancel, suspend, refuse, or restrict subscriptions or transactions in circumstances such as:
- fraud or suspected fraud;
- abuse of promotions or credits;
- misuse of the Service;
- violation of our Terms;
- payment reversal risk;
- legal or compliance concerns;
- technical pricing error;
- duplicate or clearly mistaken purchase.

If we cancel a subscription due to our own confirmed billing or provisioning error, we may provide an appropriate refund, credit, or account adjustment. If we terminate or suspend for fraud, abuse, or material breach, we may deny a refund to the extent permitted by law.

## 22. Service Credits and Promotional Adjustments

In some cases, instead of or in addition to a monetary refund, we may offer:
- service credit;
- billing credit;
- extension of subscription days;
- promotional coupon;
- upgraded access for a limited period;
- account-level adjustment.

Any such credit:
- may be non-transferable;
- may have expiration conditions;
- may not be redeemable for cash unless required by law.

## 23. Taxes, Fees, and Currency

Subscription charges may include or exclude taxes depending on local law, billing setup, and invoice presentation.

Refunds may apply to the gross amount, net amount, tax component, or adjusted amount depending on:
- the original transaction;
- whether tax was remitted;
- legal requirements;
- gateway limitations;
- currency conversion effects.

If a payment involved currency conversion, bank charges, forex differences, or intermediary fees, the refunded amount received may differ from the originally debited amount due to external financial factors beyond our control.

## 24. Account Deletion Does Not Automatically Cancel Billing

Deleting the app, uninstalling a mobile application, logging out, or ceasing to use the Service does not automatically cancel an active paid subscription.

Similarly, requesting account deletion may require billing closure steps to be completed first. You must ensure that cancellation is properly processed through the designated subscription controls or by contacting support.

## 25. Plan Access After Cancellation

After cancellation:
- paid features may remain available until the end of the current paid period unless immediate cancellation applies;
- after expiry, your account may revert to the Free Plan or limited-access mode;
- data may remain stored according to our retention practices;
- some vitals, exports, reports, or advanced features may become unavailable, limited, or read-only.

## 26. Exceptional Circumstances

We may consider exceptions to this Policy in our discretion, including in cases involving:
- verified billing errors;
- severe platform outage;
- legal obligations;
- duplicate or mistaken transactions;
- account compromise;
- compassionate or consumer-rights considerations.

Any exception granted in one case does not establish a binding precedent for future cases.

## 27. Contact for Cancellation and Refund Requests

For all cancellation, billing, and refund queries, please contact:

**VitalTrack Billing Support**  
Email: mail@altty.com
Support Email: mail@altty.com  
Website: https://www.vitaltrack.in  
Billing Helpdesk WhatsApp: +91 798 158 5715
Registered Business Address: AaVi Technos, 150/2RT, Vijaya Nagar Colony, Hyderabad, INDIA - 500057

Please include your registered email address and transaction reference in all billing communications to help us process your request faster.

## 28. Changes to This Policy

We may update this Refund & Cancellation Policy from time to time to reflect changes in:
- our plans or pricing;
- payment gateway integrations;
- legal requirements;
- operational processes;
- refund handling workflows.

Any updated version will be posted on our website or app with a revised “Last updated” date. Continued use of the Service after the effective date of the revised Policy means you acknowledge the updated terms, subject to applicable law."""
    },
    "about": {
        "title": "About VitalTrack",
        "content": """# About VitalTrack\n\n**Welcome to VitalTrack**

At VitalTrack, we believe that better health awareness begins with better daily visibility.

VitalTrack is a digital health and wellness tracking platform designed to help individuals record, organize, monitor, and better understand their day-to-day health vitals in one secure and easy-to-use place. Our goal is simple: make personal health tracking more structured, more understandable, and more accessible for everyday users who want to stay informed about their routines, patterns, and wellness trends.

We built VitalTrack for people who want a practical and reliable way to maintain daily records of important body and lifestyle measurements without relying on scattered notebooks, spreadsheets, disconnected apps, or memory alone.

## Our Mission

Our mission is to help people build consistent health awareness through simple, organized, and meaningful tracking of daily wellness vitals.

We want users to feel more confident about:
- recording their health data regularly;
- spotting patterns over time;
- staying consistent with reminders;
- preparing accurate summaries for personal review;
- sharing organized reports with healthcare professionals, family members, trainers, or caregivers when they choose to do so.

We believe that when people can see their own trends clearly, they are better equipped to ask informed questions, build healthier habits, and make more thoughtful decisions in collaboration with qualified medical professionals.

## What VitalTrack Does

VitalTrack is designed to support the daily tracking of 12 important health and wellness vitals:

- Blood Glucose Level
- Blood Oxygen Level
- Blood Pressure
- Body Mass Index (BMI)
- Body Temperature
- Heart Rate (Pulse)
- Respiratory Rate
- Sleep Duration
- Physical Activity
- Waist Circumference
- Weight
- Hydration Level

Our platform allows users to:
- enter daily vital records in a structured tabular format;
- review historical logs by day, week, month, and longer periods;
- visualize personal trends using charts tailored to each vital;
- receive reminders through email, push, or in-app notifications;
- export reports in PDF and CSV formats;
- share reports through controlled links where supported;
- manage tracked vitals based on their subscription plan;
- access the platform across responsive web and app-ready experiences.

## Why We Built VitalTrack

Many people want to monitor their health more closely, but they often face common problems:
- information is spread across notebooks, spreadsheets, devices, and apps;
- daily tracking becomes inconsistent without reminders;
- historical data is hard to interpret without visual trends;
- exported records are not always easy to share with a doctor or family member;
- many tools are either too clinical, too limited, or too difficult for regular daily use.

VitalTrack was created to solve these practical challenges by combining simplicity, structure, consistency, and usability in one platform.

We aim to bridge the gap between raw health data and useful daily tracking by giving users a clean dashboard experience, a practical table-based logging system, meaningful chart views, multilingual access, and report exports that are easier to review and share.

## Our Approach

Our approach is based on five core principles:

### 1. Clarity
Health tracking should not feel confusing or overwhelming. We focus on making daily entry, trend analysis, and report generation easy to understand.

### 2. Consistency
Good tracking depends on regular habits. That is why reminders, repeatable logging workflows, and organized date-based views are central to the platform.

### 3. User Control
Users should be able to decide what they track, what they export, what they share, and when they receive notifications.

### 4. Privacy and Respect
Health-related information is personal. We are committed to handling user information with care, transparency, and appropriate safeguards.

### 5. Continuous Improvement
We want VitalTrack to evolve based on real user needs, responsible product design, and improvements in usability, security, and reliability.

Health app trust guidance emphasizes transparent communication, credible information, clear explanation of data practices, and visible disclosure of what an app does and does not do, which is why clarity and transparency are central to how we present VitalTrack. [web:76][web:77][web:85]

## Who VitalTrack Is For

VitalTrack is intended for a wide range of users who want to maintain organized personal wellness records, including:
- individuals tracking day-to-day health routines;
- people trying to maintain consistency in monitoring selected vitals;
- families helping loved ones keep structured records;
- wellness-focused users who want visual trends over time;
- fitness-conscious users monitoring body and activity-related measures;
- caregivers who assist with record organization;
- users preparing summaries for physician visits or personal review.

Our platform is designed to be useful for both light everyday tracking and more committed long-term recordkeeping.

## What Makes VitalTrack Different

We focus on practical usability instead of unnecessary complexity.

Key aspects of the VitalTrack experience include:
- a table-based daily entry system with vitals listed in rows and dates shown in columns;
- grouped monthly views for easier navigation of large datasets;
- charts tailored to the measurement type of each vital;
- freemium access for lighter use and paid plans for broader tracking needs;
- exportable PDF and CSV reports;
- sharable reporting features;
- multilingual support;
- responsive design for desktop and mobile use;
- admin and analytics capabilities for platform governance and improvement.

Rather than treating tracking as a one-time task, we designed VitalTrack as an ongoing daily-use system that fits into real routines.

## Trust, Transparency, and Responsibility

We understand that digital health platforms must earn user trust.

Industry guidance for mobile health apps emphasizes transparency about what information supports the app, what data is collected, how it is used, and where users can find that information, including in an accessible “About” section. [web:76]

That is why we aim to be transparent about:
- what the platform is built to do;
- what kinds of data users enter;
- how information may be stored and processed;
- what security and privacy practices guide our product design;
- what limitations apply to the Service.

We strive to communicate clearly, avoid misleading claims, and present product information in plain language wherever possible. Digital trust guidance in healthcare also emphasizes transparent communication, ethical data handling, privacy, and user confidence as core pillars of trusted digital health experiences. [web:77]

## Data Privacy and Security Mindset

We recognize that health-related information deserves careful handling.

Our platform is developed with a privacy-conscious and security-aware mindset that prioritizes:
- controlled access to user accounts;
- protection of sensitive information;
- responsible data handling practices;
- secure authentication flows;
- auditability and accountability in system operations;
- careful management of exports and report sharing features.

Healthcare SaaS trust and compliance discussions consistently emphasize encryption, access controls, audit logging, and ongoing security processes as foundational elements when handling sensitive health information. [web:77][web:78][web:83]

Our policies, controls, and technical implementation are intended to evolve over time as the platform grows, regulatory expectations change, and user needs become more sophisticated.

## Important Medical Disclaimer

VitalTrack is designed for personal tracking, organization, and informational review.

VitalTrack is **not** a medical device, emergency monitoring service, diagnostic system, or substitute for professional medical advice, diagnosis, or treatment.

The charts, reminders, summaries, and trends available through the platform are intended to help users record and review their information more clearly. They are not intended to replace qualified medical judgment.

Users should always consult a licensed healthcare professional for medical concerns, treatment decisions, diagnosis, or emergency situations.

Transparency guidance for mHealth apps emphasizes that app descriptions and content should be truthful, fair, easy to find, and clear about what the app does and does not establish scientifically. [web:76]

## Our Product Vision

Our long-term vision is to make VitalTrack a reliable digital companion for structured health awareness.

As the platform evolves, we aim to continue improving:
- usability and speed;
- multilingual accessibility;
- chart intelligence and clearer summaries;
- report quality and sharing controls;
- reminder flexibility;
- subscription value;
- data portability;
- integrations with future health ecosystems where appropriate.

We want to build a product that remains simple enough for daily use, yet powerful enough to support meaningful long-term tracking.

## Our Commitment to Users

We are committed to:
- building a product that is practical and user-friendly;
- treating user data with seriousness and respect;
- communicating clearly about features and limitations;
- improving reliability, transparency, and accessibility over time;
- creating a platform that supports everyday users, families, and wellness-focused individuals in a responsible way.

We know that health tracking is personal. Our responsibility is to provide a platform that helps users stay organized, informed, and in control of their own records.

## Contact Us

If you have questions about VitalTrack, our mission, our platform, or our policies, you can contact us at:

**VitalTrack Team**  
Email: mail@altty.com  
Privacy Contact: mail@altty.com  
Website: https://www.vitaltrack.in  
Registered Address: AaVi Technos, 150/2RT, Vijaya Nagar Colony, Hyderabad, INDIA - 500057

We appreciate the trust users place in us and aim to continue building VitalTrack with clarity, responsibility, and long-term usefulness in mind."""
    },
}
