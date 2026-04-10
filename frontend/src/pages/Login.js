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
    <div className="min-h-screen flex items-center justify-center bg-[#FAFAF9] px-4">
      <div className="w-full max-w-md animate-fade-in-up">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 mb-6">
            <Heartbeat weight="duotone" className="w-8 h-8 text-[#2D4A3E]" />
            <span className="text-xl font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Welcome back</h1>
          <p className="text-sm text-[#6E6E6A] mt-1">Sign in to your account</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-white border border-[#EAE7E1] rounded-2xl p-8 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-4" data-testid="login-error">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-sm text-[#2C2C2A]">Email</Label>
              <Input
                id="email" type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com" required data-testid="login-email-input"
                className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9] focus:ring-[#2D4A3E]/20 focus:border-[#2D4A3E]"
              />
            </div>
            <div>
              <Label htmlFor="password" className="text-sm text-[#2C2C2A]">Password</Label>
              <Input
                id="password" type="password" value={password} onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password" required data-testid="login-password-input"
                className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9] focus:ring-[#2D4A3E]/20 focus:border-[#2D4A3E]"
              />
            </div>
          </div>
          <Button
            type="submit" disabled={loading} data-testid="login-submit-btn"
            className="w-full mt-6 rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white py-3"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
          <p className="text-center text-sm text-[#6E6E6A] mt-4">
            Don't have an account?{' '}
            <Link to="/register" className="text-[#2D4A3E] font-medium hover:underline" data-testid="login-register-link">
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
