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
