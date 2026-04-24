import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { formatApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heartbeat } from '@phosphor-icons/react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(email, password);
      if (['admin', 'super_admin'].includes(user.role)) {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
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
          <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Welcome back</h1>
          <p className="text-sm text-[#64748B] mt-1">Sign in to your account</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-white border border-[#E2E8F0] rounded-2xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-4" data-testid="login-error">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-sm text-[#0F172A]">Email</Label>
              <Input
                id="email" type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com" required data-testid="login-email-input"
                className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]"
              />
            </div>
            <div>
              <Label htmlFor="password" className="text-sm text-[#0F172A]">Password</Label>
              <Input
                id="password" type="password" value={password} onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password" required data-testid="login-password-input"
                className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]"
              />
            </div>
          </div>
          <Button
            type="submit" disabled={loading} data-testid="login-submit-btn"
            className="w-full mt-6 rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white py-3"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
          <div className="text-center mt-3">
            <Link to="/forgot-password" className="text-sm text-[#0EA5E9] hover:underline" data-testid="forgot-password-link">
              Forgot your password?
            </Link>
          </div>
          <p className="text-center text-sm text-[#64748B] mt-3">
            Don't have an account?{' '}
            <Link to="/register" className="text-[#0EA5E9] font-medium hover:underline" data-testid="login-register-link">
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
