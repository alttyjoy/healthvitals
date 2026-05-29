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
        "content": """# Terms of Service\n\n**Last updated: April 2026**\n\n## 1. Acceptance of Terms\nBy accessing or using VitalTrack ("Service"), you agree to be bound by these Terms of Service.\n\n## 2. Description of Service\nVitalTrack is a health vitals tracking platform for informational and personal tracking purposes only.\n\n## 3. Medical Disclaimer\nVitalTrack is NOT a medical device. Always consult a qualified healthcare professional.\n\n## 4. User Accounts\n- Accurate information required\n- You are responsible for account security\n- Must be 18+ to create an account\n\n## 5. Subscription Plans\n- Free, Standard (₹299/month), and Premium (₹499/month)\n- Plan features and pricing may change with 30 days notice\n\n## 6. Payment Terms\nPayments processed through Razorpay and PayU.In. All prices in INR.\n\n## 7. Data Privacy\nYour health data is personal. We handle it per our Privacy Policy.\n\n## 8. Contact\nsupport@vitaltrack.in"""
    },
    "privacy": {
        "title": "Privacy Policy",
        "content": """# Privacy Policy\n\n**Last updated: April 2026**\n\n## 1. Information We Collect\n- Personal: Name, email\n- Health Data: Daily vital readings\n- Usage Data: Login timestamps, device info\n\n## 2. How We Use Your Data\n- Provide and improve service\n- Generate charts and reports\n- Send reminders (with consent)\n\n## 3. Data Security\nEncryption in transit, industry-standard practices.\n\n## 4. Data Sharing\nWe do NOT sell your health data.\n\n## 5. Your Rights\n- Access, Export, Delete, Correct, Opt-out\n\n## 6. Contact\nprivacy@vitaltrack.in"""
    },
    "refund": {
        "title": "Refund & Cancellation Policy",
        "content": """# Refund & Cancellation Policy\n\n**Last updated: April 2026**\n\n## 1. Cancellation\n- Cancel anytime from Billing page\n- Reverts to Free plan after period ends\n\n## 2. Refund\n- Full refund within 7 days of initial purchase\n- Annual plans prorated for unused months\n\n## 3. How to Request\nContact support@vitaltrack.in with transaction ID.\n\n## 4. Contact\nbilling@vitaltrack.in"""
    },
    "about": {
        "title": "About VitalTrack",
        "content": """# About VitalTrack\n\n## Our Mission\nEmpower individuals to take control of their health through simple, consistent daily tracking.\n\n## What We Do\nTrack 12 essential health vitals. Visualize trends, generate reports, share with providers.\n\n## Our Approach\n- Simplicity: Less than a minute daily\n- Insights: Smart analysis\n- Privacy: Your data is yours\n- Accessibility: English, Hindi, Telugu\n\n## Contact\nsupport@vitaltrack.in"""
    },
}
