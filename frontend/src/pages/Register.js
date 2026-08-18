import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { formatApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heartbeat } from '@phosphor-icons/react';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setLoading(true);
    try {
      await register(name, email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] px-4">
      <div className="w-full max-w-md animate-fade-in-up">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 mb-6">
            <Heartbeat weight="duotone" className="w-8 h-8 text-[#0EA5E9]" />
            <span className="text-xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Create your account</h1>
          <p className="text-sm text-[#64748B] mt-1">Start tracking your health for free</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-white border border-[#E2E8F0] rounded-2xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-4" data-testid="register-error">{error}</div>
          )}
          {/* Google Sign-Up */}
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
              const redirectUrl = window.location.origin + '/dashboard';
              window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
            }}
            data-testid="google-register-btn"
            className="w-full rounded-xl border-[#E2E8F0] text-[#0F172A] hover:bg-[#F8FAFC] py-3 mb-5 flex items-center justify-center gap-2.5 font-medium"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </Button>
          <div className="relative mb-5">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-[#E2E8F0]" /></div>
            <div className="relative flex justify-center text-xs"><span className="bg-white px-3 text-[#94A3B8]">or register with email</span></div>
          </div>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-sm text-[#0F172A]">Full Name</Label>
              <Input id="name" value={name} onChange={e => setName(e.target.value)} placeholder="John Doe" required data-testid="register-name-input"
                className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]" />
            </div>
            <div>
              <Label htmlFor="email" className="text-sm text-[#0F172A]">Email</Label>
              <Input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required data-testid="register-email-input"
                className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]" />
            </div>
            <div>
              <Label htmlFor="password" className="text-sm text-[#0F172A]">Password</Label>
              <Input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min 6 characters" required data-testid="register-password-input"
                className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]" />
            </div>
          </div>
          <Button type="submit" disabled={loading} data-testid="register-submit-btn"
            className="w-full mt-6 rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white py-3">
            {loading ? 'Creating account...' : 'Create Account'}
          </Button>
          <p className="text-center text-sm text-[#64748B] mt-4">
            Already have an account? <Link to="/login" className="text-[#0EA5E9] font-medium hover:underline" data-testid="register-login-link">Sign in</Link>
          </p>
        </form>
        <p className="text-center text-xs text-[#64748B] mt-6">
          For informational tracking only. Not a medical device. Consult your healthcare provider.
        </p>
      </div>
    </div>
  );
}
