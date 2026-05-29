import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Heartbeat, ChartLine, Table, FileArrowDown, Bell, ShieldCheck,
  Check, ArrowRight, CaretDown, Star, List, X
} from '@phosphor-icons/react';
import { useState } from 'react';

const features = [
  { icon: Table, title: 'Daily Tracker', desc: 'Spreadsheet-style entry for all your vitals. Quick, intuitive, with inline editing.' },
  { icon: ChartLine, title: 'Smart Charts', desc: 'Tailored visualizations for each vital with trend analysis and threshold indicators.' },
  { icon: FileArrowDown, title: 'Export Reports', desc: 'Download CSV or PDF reports. Share securely with your healthcare provider.' },
  { icon: Bell, title: 'Reminders', desc: 'Never miss a reading. Set custom reminders for each vital you track.' },
  { icon: ShieldCheck, title: 'Secure & Private', desc: 'Your health data is encrypted and protected. GDPR-ready architecture.' },
  { icon: Heartbeat, title: 'Health Insights', desc: 'Rule-based analysis helps you spot trends and stay on top of your health.' },
];

const plans = [
  { key: 'free', name: 'Free', price: 0, period: 'forever', vitals: 2, features: ['Track any 2 vitals', '7-day chart history', 'Basic CSV export', 'Basic reminders'], popular: false },
  { key: 'standard', name: 'Standard', price: 299, period: '/month', vitals: 6, features: ['Track any 6 vitals', 'Full 1-year history', 'CSV & PDF export', 'Shareable reports', 'Advanced reminders'], popular: true },
  { key: 'premium', name: 'Premium', price: 499, period: '/month', vitals: 12, features: ['Track all 12 vitals', 'Unlimited history', 'All export formats', 'Full sharing', 'Priority support', 'Advanced analytics'], popular: false },
];

const faqs = [
  { q: 'What vitals can I track?', a: 'VitalTrack supports 12 health vitals: Blood Glucose, Blood Oxygen, Blood Pressure, BMI, Body Temperature, Heart Rate, Respiratory Rate, Sleep Duration, Physical Activity, Waist Circumference, Weight, and Hydration Level.' },
  { q: 'Is my health data secure?', a: 'Absolutely. We use encrypted connections, secure authentication, and follow privacy-by-design principles. Your data is never shared with third parties.' },
  { q: 'Can I export my data?', a: 'Yes! Free users can export CSV files. Standard and Premium users can also export PDF reports and share secure links with healthcare providers.' },
  { q: 'Is this a medical device?', a: 'No. VitalTrack is a tracking and informational tool. It does not provide medical diagnosis or treatment recommendations. Always consult your healthcare provider.' },
  { q: 'How often should I log my vitals?', a: 'We recommend logging daily for the most accurate trends and insights. Consistent daily tracking helps identify patterns your doctor can use for better care decisions.' },
  { q: 'Can I share my reports with my doctor?', a: 'Yes! Standard and Premium users can generate password-protected shareable links. Your doctor can view your vitals, charts, and trends without needing an account.' },
  { q: 'What happens if I downgrade my plan?', a: 'Your historical data is always preserved. If you downgrade, excess enabled vitals become read-only. You can re-enable them anytime by upgrading again.' },
  { q: 'Do you support multiple languages?', a: 'Yes! VitalTrack is available in English, Hindi, and Telugu. You can switch languages anytime from your Settings page.' },
];

export default function Landing() {
  const { user } = useAuth();
  const [openFaq, setOpenFaq] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 glass-nav border-b border-[#E2E8F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12 flex items-center justify-between h-14 sm:h-16">
          <Link to="/" className="flex items-center gap-2" data-testid="nav-logo">
            <Heartbeat weight="duotone" className="w-6 h-6 sm:w-7 sm:h-7 text-[#0EA5E9]" />
            <span className="text-base sm:text-lg font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-[#64748B]">
            <a href="#features" className="hover:text-[#0F172A] transition-colors">Features</a>
            <a href="#pricing" className="hover:text-[#0F172A] transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-[#0F172A] transition-colors">FAQ</a>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            {user ? (
              <Link to="/dashboard">
                <Button className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-4 sm:px-6 text-sm" data-testid="go-to-dashboard-btn">
                  Dashboard <ArrowRight className="w-4 h-4 ml-1 hidden sm:inline" />
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login" className="hidden sm:block">
                  <Button variant="ghost" className="text-[#64748B] hover:text-[#0F172A] text-sm" data-testid="nav-login-btn">Sign In</Button>
                </Link>
                <Link to="/register">
                  <Button className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-4 sm:px-6 text-sm" data-testid="nav-register-btn">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
            <button
              className="md:hidden p-1.5 rounded-lg hover:bg-[#E2E8F0] transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-nav-toggle"
            >
              {mobileMenuOpen ? <X className="w-5 h-5 text-[#0F172A]" /> : <List className="w-5 h-5 text-[#0F172A]" />}
            </button>
          </div>
        </div>
        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#E2E8F0] bg-white/95 backdrop-blur-md animate-fade-in">
            <div className="px-4 py-3 space-y-1">
              <a href="#features" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2.5 text-sm text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC] rounded-lg">Features</a>
              <a href="#pricing" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2.5 text-sm text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC] rounded-lg">Pricing</a>
              <a href="#faq" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2.5 text-sm text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC] rounded-lg">FAQ</a>
              {!user && (
                <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2.5 text-sm text-[#0EA5E9] font-medium hover:bg-[#F8FAFC] rounded-lg">Sign In</Link>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Hero */}
      <section className="pt-24 sm:pt-32 pb-16 sm:pb-24 px-4 sm:px-6 md:px-12 lg:px-24 relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `url("https://static.prod-images.emergentagent.com/jobs/5b2bf7cd-4a4c-4ab4-a4a8-7fc4ef4c140f/images/682a0b7f8e530af3f32d69f922f39c29da09a79d7e77fbe3af46054e7768646c.png")`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div className="max-w-7xl mx-auto relative">
          <div className="max-w-3xl animate-fade-in-up">
            <Badge className="bg-[#0EA5E9]/10 text-[#0EA5E9] border-0 rounded-full px-4 py-1.5 text-xs tracking-wide font-medium mb-6 hover:bg-[#0EA5E9]/15 cursor-default">
              Health Vitals Tracking Platform
            </Badge>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl tracking-tight font-light text-[#0F172A] mb-4 sm:mb-6 leading-[1.1]" style={{ fontFamily: 'Outfit' }}>
              Track Your Health,<br />
              <span className="font-medium text-[#0EA5E9]">Every Single Day</span>
            </h1>
            <p className="text-base sm:text-lg text-[#64748B] leading-relaxed mb-8 sm:mb-10 max-w-xl">
              Monitor 12 health vitals with an intuitive daily tracker. Visualize trends, export reports, and share insights with your healthcare provider.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <Link to="/register">
                <Button className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6 sm:px-8 py-3 sm:py-3.5 text-sm sm:text-base shadow-[0_4px_14px_rgba(14,165,233,0.4)] hover:shadow-[0_6px_20px_rgba(14,165,233,0.3)] transition-all hover:-translate-y-0.5 w-full sm:w-auto" data-testid="hero-cta-btn">
                  Start Tracking Free <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <a href="#features">
                <Button variant="outline" className="rounded-full border-[#E2E8F0] text-[#64748B] px-6 sm:px-8 py-3 sm:py-3.5 text-sm sm:text-base hover:bg-[#0EA5E9]/10 hover:text-[#0EA5E9] hover:border-[#0EA5E9]/30 w-full sm:w-auto transition-all" data-testid="hero-learn-more-btn">
                  Learn More
                </Button>
              </a>
            </div>
          </div>
          <div className="mt-10 sm:mt-16 grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-6 animate-fade-in-up stagger-2">
            {[{ n: '12', l: 'Health Vitals' }, { n: '3', l: 'Flexible Plans' }, { n: '24/7', l: 'Access Anywhere' }, { n: '100%', l: 'Data Privacy' }].map((s, i) => (
              <div key={i} className="bg-white border border-[#E2E8F0] rounded-xl sm:rounded-2xl p-4 sm:p-6 text-center shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
                <div className="text-2xl sm:text-3xl font-semibold text-[#0EA5E9] mb-1" style={{ fontFamily: 'Outfit' }}>{s.n}</div>
                <div className="text-xs sm:text-sm text-[#64748B]">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16 sm:py-24 px-4 sm:px-6 md:px-12 lg:px-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10 sm:mb-16 animate-fade-in-up">
            <span className="text-xs tracking-[0.2em] uppercase text-[#0EA5E9] font-semibold">Features</span>
            <h2 className="text-3xl sm:text-4xl tracking-tight font-medium text-[#0F172A] mt-3" style={{ fontFamily: 'Outfit' }}>
              Everything You Need to Track Your Health
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-8">
            {features.map((f, i) => (
              <div key={i} className={`bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl sm:rounded-2xl p-6 sm:p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg animate-fade-in-up stagger-${i % 3 + 1}`}>
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-[#0EA5E9]/10 flex items-center justify-center mb-4 sm:mb-5">
                  <f.icon weight="duotone" className="w-5 h-5 sm:w-6 sm:h-6 text-[#0EA5E9]" />
                </div>
                <h3 className="text-lg font-medium text-[#0F172A] mb-2" style={{ fontFamily: 'Outfit' }}>{f.title}</h3>
                <p className="text-sm text-[#64748B] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-16 sm:py-24 px-4 sm:px-6 md:px-12 lg:px-24">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10 sm:mb-16">
            <span className="text-xs tracking-[0.2em] uppercase text-[#0EA5E9] font-semibold">Pricing</span>
            <h2 className="text-2xl sm:text-3xl md:text-4xl tracking-tight font-medium text-[#0F172A] mt-3" style={{ fontFamily: 'Outfit' }}>
              Simple, Transparent Pricing
            </h2>
            <p className="text-base text-[#64748B] mt-3">Start free. Upgrade when you need more.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-8 max-w-5xl mx-auto">
            {plans.map((plan) => (
              <div
                key={plan.key}
                data-testid={`pricing-card-${plan.key}`}
                className={`relative bg-white border rounded-xl sm:rounded-2xl p-6 sm:p-8 transition-all duration-300 hover:-translate-y-1 ${
                  plan.popular ? 'border-[#0EA5E9] shadow-lg scale-[1.02]' : 'border-[#E2E8F0] shadow-[0_8px_30px_rgb(0,0,0,0.04)]'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-[#0EA5E9] text-white border-0 rounded-full px-4 py-1 text-xs">
                      <Star weight="fill" className="w-3 h-3 mr-1" /> Most Popular
                    </Badge>
                  </div>
                )}
                <h3 className="text-xl font-medium text-[#0F172A] mb-2" style={{ fontFamily: 'Outfit' }}>{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-4xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>
                    {plan.price === 0 ? 'Free' : `₹${plan.price}`}
                  </span>
                  {plan.price > 0 && <span className="text-sm text-[#64748B]">{plan.period}</span>}
                </div>
                <p className="text-sm text-[#64748B] mb-6">Track up to {plan.vitals} vitals</p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-sm text-[#0F172A]">
                      <Check weight="bold" className="w-4 h-4 text-[#10B981] mt-0.5 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link to="/register">
                  <Button
                    data-testid={`pricing-cta-${plan.key}`}
                    className={`w-full rounded-full py-3 transition-all ${
                      plan.popular
                        ? 'bg-[#0EA5E9] hover:bg-[#0284C7] text-white'
                        : 'bg-[#E2E8F0] hover:bg-[#DEDCD5] text-[#0F172A]'
                    }`}
                  >
                    {plan.price === 0 ? 'Get Started' : 'Subscribe Now'}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-16 sm:py-24 px-4 sm:px-6 md:px-12 lg:px-24 bg-white">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <span className="text-xs tracking-[0.2em] uppercase text-[#0EA5E9] font-semibold">FAQ</span>
            <h2 className="text-3xl sm:text-4xl tracking-tight font-medium text-[#0F172A] mt-3" style={{ fontFamily: 'Outfit' }}>
              Common Questions
            </h2>
          </div>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-[#E2E8F0] rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  data-testid={`faq-${i}`}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-[#F8FAFC] transition-colors"
                >
                  <span className="text-sm font-medium text-[#0F172A]">{faq.q}</span>
                  <CaretDown className={`w-4 h-4 text-[#64748B] transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                {openFaq === i && (
                  <div className="px-5 pb-5 text-sm text-[#64748B] leading-relaxed animate-fade-in">{faq.a}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 md:px-12 lg:px-24">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-[#0EA5E9] to-[#0284C7] rounded-2xl sm:rounded-3xl p-8 sm:p-12 md:p-16 text-center shadow-[0_20px_60px_rgba(14,165,233,0.25)]">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-medium text-white mb-3 sm:mb-4" style={{ fontFamily: 'Outfit' }}>
            Start Your Health Journey Today
          </h2>
          <p className="text-base text-white/70 mb-8 max-w-lg mx-auto">
            Join thousands tracking their health vitals daily. Free to start, upgrade anytime.
          </p>
          <Link to="/register">
            <Button className="rounded-full bg-white text-[#0EA5E9] hover:bg-white/90 px-8 py-3.5 text-base shadow-lg" data-testid="cta-get-started-btn">
              Get Started Free <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 sm:py-12 px-4 sm:px-6 md:px-12 lg:px-24 border-t border-[#E2E8F0]">
        <div className="max-w-7xl mx-auto flex flex-col items-center gap-4 sm:gap-6 md:flex-row md:justify-between">
          <div className="flex items-center gap-2.5">
            <Heartbeat weight="duotone" className="w-6 h-6 text-[#0EA5E9]" />
            <span className="text-base font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </div>
          <div className="flex flex-wrap justify-center gap-4 sm:gap-6 text-sm text-[#64748B]">
            <a href="#features" className="hover:text-[#0F172A] transition-colors">Features</a>
            <a href="#pricing" className="hover:text-[#0F172A] transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-[#0F172A] transition-colors">FAQ</a>
            <Link to="/page/terms" className="hover:text-[#0F172A] transition-colors" data-testid="footer-terms">Terms</Link>
            <Link to="/page/privacy" className="hover:text-[#0F172A] transition-colors" data-testid="footer-privacy">Privacy</Link>
            <Link to="/page/refund" className="hover:text-[#0F172A] transition-colors" data-testid="footer-refunds">Refunds</Link>
            <Link to="/page/about" className="hover:text-[#0F172A] transition-colors" data-testid="footer-about">About</Link>
          </div>
          <p className="text-xs text-[#64748B]">
            Not a medical device. For informational tracking only. Consult your healthcare provider.
          </p>
        </div>
      </footer>
    </div>
  );
}
