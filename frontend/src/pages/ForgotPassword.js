import { useState } from 'react';
import { Link } from 'react-router-dom';
import api, { formatApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heartbeat, ArrowLeft } from '@phosphor-icons/react';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/auth/forgot-password', { email });
      setSent(true);
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
          <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Reset your password</h1>
          <p className="text-sm text-[#6E6E6A] mt-1">Enter your email and we'll send you a reset link</p>
        </div>
        <div className="bg-white border border-[#EAE7E1] rounded-2xl p-8 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
          {sent ? (
            <div data-testid="forgot-password-success">
              <div className="bg-[#2D4A3E]/10 text-[#2D4A3E] text-sm px-4 py-3 rounded-lg mb-4">
                If an account with that email exists, a password reset link has been sent. Check your inbox.
              </div>
              <p className="text-xs text-[#6E6E6A] mb-4">
                Note: If SMTP is not configured yet, the reset token is logged on the server. Contact your admin for the reset link.
              </p>
              <Link to="/login">
                <Button variant="outline" className="w-full rounded-full border-[#EAE7E1]" data-testid="back-to-login-btn">
                  <ArrowLeft className="w-4 h-4 mr-2" /> Back to Sign In
                </Button>
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-4" data-testid="forgot-password-error">{error}</div>
              )}
              <div>
                <Label htmlFor="email" className="text-sm text-[#2C2C2A]">Email</Label>
                <Input
                  id="email" type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com" required data-testid="forgot-email-input"
                  className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9] focus:ring-[#2D4A3E]/20 focus:border-[#2D4A3E]"
                />
              </div>
              <Button type="submit" disabled={loading} data-testid="forgot-submit-btn"
                className="w-full mt-6 rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white py-3">
                {loading ? 'Sending...' : 'Send Reset Link'}
              </Button>
              <p className="text-center text-sm text-[#6E6E6A] mt-4">
                <Link to="/login" className="text-[#2D4A3E] font-medium hover:underline" data-testid="forgot-back-link">
                  <ArrowLeft className="w-3 h-3 inline mr-1" /> Back to Sign In
                </Link>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
