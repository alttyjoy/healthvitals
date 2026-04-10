import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

const ThemeContext = createContext(null);

const defaultTranslations = {
  app_name: "VitalTrack", dashboard: "Dashboard", daily_tracker: "Daily Tracker",
  charts_trends: "Charts & Trends", reports: "Reports", billing: "Billing",
  settings: "Settings", admin_panel: "Admin Panel", sign_out: "Sign Out",
  welcome_back: "Welcome back", active_vitals: "Active Vitals", todays_entries: "Today's Entries",
  this_week: "This Week", plan: "Plan", health_insights: "Health Insights",
  quick_actions: "Quick Actions", your_vitals: "Your Vitals", log_todays_vitals: "Log Today's Vitals",
  view_trends: "View Trends", export_report: "Export Report", enable_vitals: "Enable Vitals",
  get_started: "Get Started", save_all: "Save All", no_vitals_enabled: "No Vitals Enabled",
  select_vital: "Select vital", date_range: "Date Range", export: "Export",
  current_plan: "Current Plan", upgrade: "Upgrade", downgrade: "Downgrade",
  switch: "Switch", profile: "Profile", manage_vitals: "Manage Vitals",
  save_profile: "Save Profile", full_name: "Full Name", email: "Email",
  password: "Password", sign_in: "Sign In", create_account: "Create Account",
  dont_have_account: "Don't have an account?", already_have_account: "Already have an account?",
  dark_mode: "Dark Mode", language: "Language", subscription_billing: "Subscription & Billing",
  reports_export: "Reports & Export", shared_reports: "Shared Reports",
  create_shared_report: "Create Shared Report", share_link: "Share Link",
  password_protected: "Password Protected", expires_in: "Expires in",
  revoke: "Revoke", copy_link: "Copy Link", normal: "Normal", warning: "Warning",
  critical: "Critical", medical_disclaimer: "For informational tracking only. Not a medical device.",
};

export function ThemeProvider({ children }) {
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true');
  const [language, setLanguage] = useState(() => localStorage.getItem('language') || 'en');
  const [translations, setTranslations] = useState(defaultTranslations);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  const loadTranslations = useCallback(async (lang) => {
    try {
      const { data } = await api.get(`/translations/${lang}`);
      setTranslations(data);
    } catch {
      setTranslations(defaultTranslations);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('language', language);
    loadTranslations(language);
  }, [language, loadTranslations]);

  const toggleDarkMode = () => setDarkMode(prev => !prev);
  const t = (key) => translations[key] || defaultTranslations[key] || key;

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode, language, setLanguage, t }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be within ThemeProvider');
  return ctx;
}
