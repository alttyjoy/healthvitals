import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Heartbeat, ChartLine, Table, FileArrowDown, Bell, ShieldCheck,
  Check, ArrowRight, CaretDown, Star
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
];

export default function Landing() {
  const { user } = useAuth();
  const [openFaq, setOpenFaq] = useState(null);

  return (
    <div className="min-h-screen bg-[#FAFAF9]">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 glass-nav border-b border-[#EAE7E1]">
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2.5" data-testid="nav-logo">
            <Heartbeat weight="duotone" className="w-7 h-7 text-[#2D4A3E]" />
            <span className="text-lg font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-[#6E6E6A]">
            <a href="#features" className="hover:text-[#2C2C2A] transition-colors">Features</a>
            <a href="#pricing" className="hover:text-[#2C2C2A] transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-[#2C2C2A] transition-colors">FAQ</a>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <Link to="/dashboard">
                <Button className="rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white px-6" data-testid="go-to-dashboard-btn">
                  Dashboard <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" className="text-[#6E6E6A] hover:text-[#2C2C2A]" data-testid="nav-login-btn">Sign In</Button>
                </Link>
                <Link to="/register">
                  <Button className="rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white px-6" data-testid="nav-register-btn">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 md:px-12 lg:px-24 relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `url("https://static.prod-images.emergentagent.com/jobs/5b2bf7cd-4a4c-4ab4-a4a8-7fc4ef4c140f/images/682a0b7f8e530af3f32d69f922f39c29da09a79d7e77fbe3af46054e7768646c.png")`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div className="max-w-7xl mx-auto relative">
          <div className="max-w-3xl animate-fade-in-up">
            <Badge className="bg-[#2D4A3E]/10 text-[#2D4A3E] border-0 rounded-full px-4 py-1.5 text-xs tracking-wide font-medium mb-6">
              Health Vitals Tracking Platform
            </Badge>
            <h1 className="text-5xl sm:text-6xl tracking-tight font-light text-[#2C2C2A] mb-6 leading-[1.1]" style={{ fontFamily: 'Outfit' }}>
              Track Your Health,<br />
              <span className="font-medium text-[#2D4A3E]">Every Single Day</span>
            </h1>
            <p className="text-lg text-[#6E6E6A] leading-relaxed mb-10 max-w-xl">
              Monitor 12 health vitals with an intuitive daily tracker. Visualize trends, export reports, and share insights with your healthcare provider.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/register">
                <Button className="rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white px-8 py-3.5 text-base shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5" data-testid="hero-cta-btn">
                  Start Tracking Free <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <a href="#features">
                <Button variant="outline" className="rounded-full border-[#EAE7E1] text-[#6E6E6A] px-8 py-3.5 text-base hover:bg-[#EAE7E1]" data-testid="hero-learn-more-btn">
                  Learn More
                </Button>
              </a>
            </div>
          </div>
          <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-6 animate-fade-in-up stagger-2">
            {[{ n: '12', l: 'Health Vitals' }, { n: '3', l: 'Flexible Plans' }, { n: '24/7', l: 'Access Anywhere' }, { n: '100%', l: 'Data Privacy' }].map((s, i) => (
              <div key={i} className="bg-white border border-[#EAE7E1] rounded-2xl p-6 text-center shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
                <div className="text-3xl font-semibold text-[#2D4A3E] mb-1" style={{ fontFamily: 'Outfit' }}>{s.n}</div>
                <div className="text-sm text-[#6E6E6A]">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 md:px-12 lg:px-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 animate-fade-in-up">
            <span className="text-xs tracking-[0.2em] uppercase text-[#2D4A3E] font-semibold">Features</span>
            <h2 className="text-3xl sm:text-4xl tracking-tight font-medium text-[#2C2C2A] mt-3" style={{ fontFamily: 'Outfit' }}>
              Everything You Need to Track Your Health
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f, i) => (
              <div key={i} className={`bg-[#FAFAF9] border border-[#EAE7E1] rounded-2xl p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg animate-fade-in-up stagger-${i % 3 + 1}`}>
                <div className="w-12 h-12 rounded-xl bg-[#2D4A3E]/10 flex items-center justify-center mb-5">
                  <f.icon weight="duotone" className="w-6 h-6 text-[#2D4A3E]" />
                </div>
                <h3 className="text-xl font-medium text-[#2C2C2A] mb-2" style={{ fontFamily: 'Outfit' }}>{f.title}</h3>
                <p className="text-sm text-[#6E6E6A] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6 md:px-12 lg:px-24">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs tracking-[0.2em] uppercase text-[#2D4A3E] font-semibold">Pricing</span>
            <h2 className="text-3xl sm:text-4xl tracking-tight font-medium text-[#2C2C2A] mt-3" style={{ fontFamily: 'Outfit' }}>
              Simple, Transparent Pricing
            </h2>
            <p className="text-base text-[#6E6E6A] mt-3">Start free. Upgrade when you need more.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {plans.map((plan) => (
              <div
                key={plan.key}
                data-testid={`pricing-card-${plan.key}`}
                className={`relative bg-white border rounded-2xl p-8 transition-all duration-300 hover:-translate-y-1 ${
                  plan.popular ? 'border-[#2D4A3E] shadow-lg scale-[1.02]' : 'border-[#EAE7E1] shadow-[0_4px_24px_rgba(0,0,0,0.02)]'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-[#2D4A3E] text-white border-0 rounded-full px-4 py-1 text-xs">
                      <Star weight="fill" className="w-3 h-3 mr-1" /> Most Popular
                    </Badge>
                  </div>
                )}
                <h3 className="text-xl font-medium text-[#2C2C2A] mb-2" style={{ fontFamily: 'Outfit' }}>{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-4xl font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>
                    {plan.price === 0 ? 'Free' : `₹${plan.price}`}
                  </span>
                  {plan.price > 0 && <span className="text-sm text-[#6E6E6A]">{plan.period}</span>}
                </div>
                <p className="text-sm text-[#6E6E6A] mb-6">Track up to {plan.vitals} vitals</p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-sm text-[#2C2C2A]">
                      <Check weight="bold" className="w-4 h-4 text-[#588157] mt-0.5 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link to="/register">
                  <Button
                    data-testid={`pricing-cta-${plan.key}`}
                    className={`w-full rounded-full py-3 transition-all ${
                      plan.popular
                        ? 'bg-[#2D4A3E] hover:bg-[#1E332A] text-white'
                        : 'bg-[#EAE7E1] hover:bg-[#DEDCD5] text-[#2C2C2A]'
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
      <section id="faq" className="py-24 px-6 md:px-12 lg:px-24 bg-white">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <span className="text-xs tracking-[0.2em] uppercase text-[#2D4A3E] font-semibold">FAQ</span>
            <h2 className="text-3xl sm:text-4xl tracking-tight font-medium text-[#2C2C2A] mt-3" style={{ fontFamily: 'Outfit' }}>
              Common Questions
            </h2>
          </div>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-[#EAE7E1] rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  data-testid={`faq-${i}`}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-[#FAFAF9] transition-colors"
                >
                  <span className="text-sm font-medium text-[#2C2C2A]">{faq.q}</span>
                  <CaretDown className={`w-4 h-4 text-[#6E6E6A] transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                {openFaq === i && (
                  <div className="px-5 pb-5 text-sm text-[#6E6E6A] leading-relaxed animate-fade-in">{faq.a}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 md:px-12 lg:px-24">
        <div className="max-w-4xl mx-auto bg-[#2D4A3E] rounded-3xl p-12 md:p-16 text-center">
          <h2 className="text-3xl sm:text-4xl font-medium text-white mb-4" style={{ fontFamily: 'Outfit' }}>
            Start Your Health Journey Today
          </h2>
          <p className="text-base text-white/70 mb-8 max-w-lg mx-auto">
            Join thousands tracking their health vitals daily. Free to start, upgrade anytime.
          </p>
          <Link to="/register">
            <Button className="rounded-full bg-white text-[#2D4A3E] hover:bg-white/90 px-8 py-3.5 text-base shadow-lg" data-testid="cta-get-started-btn">
              Get Started Free <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 md:px-12 lg:px-24 border-t border-[#EAE7E1]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <Heartbeat weight="duotone" className="w-6 h-6 text-[#2D4A3E]" />
            <span className="text-base font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </div>
          <div className="flex flex-wrap gap-6 text-sm text-[#6E6E6A]">
            <a href="#features" className="hover:text-[#2C2C2A] transition-colors">Features</a>
            <a href="#pricing" className="hover:text-[#2C2C2A] transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-[#2C2C2A] transition-colors">FAQ</a>
          </div>
          <p className="text-xs text-[#6E6E6A]">
            Not a medical device. For informational tracking only. Consult your healthcare provider.
          </p>
        </div>
      </footer>
    </div>
  );
}
