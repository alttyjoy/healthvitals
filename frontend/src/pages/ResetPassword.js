import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api, { formatApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heartbeat, CheckCircle } from '@phosphor-icons/react';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    if (password !== confirm) { setError('Passwords do not match'); return; }
    setLoading(true);
    try {
      await api.post('/auth/reset-password', { token, password });
      setSuccess(true);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] px-4">
        <div className="text-center">
          <p className="text-[#64748B] mb-4">Invalid or missing reset token.</p>
          <Link to="/forgot-password" className="text-[#0EA5E9] font-medium hover:underline">Request a new reset link</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] px-4">
      <div className="w-full max-w-md animate-fade-in-up">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 mb-6">
            <Heartbeat weight="duotone" className="w-8 h-8 text-[#0EA5E9]" />
            <span className="text-xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>VitalTrack</span>
          </Link>
          <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Set new password</h1>
          <p className="text-sm text-[#64748B] mt-1">Choose a strong password for your account</p>
        </div>
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          {success ? (
            <div className="text-center" data-testid="reset-success">
              <CheckCircle weight="duotone" className="w-12 h-12 text-[#10B981] mx-auto mb-3" />
              <p className="text-[#0F172A] font-medium mb-2">Password reset successfully!</p>
              <Link to="/login">
                <Button className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6 mt-3" data-testid="reset-login-btn">
                  Sign In
                </Button>
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-4" data-testid="reset-error">{error}</div>
              )}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="password" className="text-sm text-[#0F172A]">New Password</Label>
                  <Input
                    id="password" type="password" value={password} onChange={e => setPassword(e.target.value)}
                    placeholder="Min 6 characters" required data-testid="reset-password-input"
                    className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]"
                  />
                </div>
                <div>
                  <Label htmlFor="confirm" className="text-sm text-[#0F172A]">Confirm Password</Label>
                  <Input
                    id="confirm" type="password" value={confirm} onChange={e => setConfirm(e.target.value)}
                    placeholder="Re-enter password" required data-testid="reset-confirm-input"
                    className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] focus:ring-[#0EA5E9]/20 focus:border-[#0EA5E9]"
                  />
                </div>
              </div>
              <Button type="submit" disabled={loading} data-testid="reset-submit-btn"
                className="w-full mt-6 rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white py-3">
                {loading ? 'Resetting...' : 'Reset Password'}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
