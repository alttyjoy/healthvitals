import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Gift, Copy, UserPlus, Check } from '@phosphor-icons/react';

export function ReferralSection() {
  const { user, refreshUser } = useAuth();
  const [referralCode, setReferralCode] = useState('');
  const [referralStats, setReferralStats] = useState({ total_referrals: 0, successful_referrals: 0 });
  const [referralInput, setReferralInput] = useState('');
  const [applyingReferral, setApplyingReferral] = useState(false);

  useEffect(() => { loadReferral(); }, []);

  const loadReferral = async () => {
    try {
      const { data } = await api.get('/referral');
      setReferralCode(data.referral_code || '');
      setReferralStats({ total_referrals: data.total_referrals || 0, successful_referrals: data.successful_referrals || 0 });
    } catch (err) { console.error('Failed to load referral:', err?.message); }
  };

  const handleApplyReferral = async () => {
    if (!referralInput.trim()) { toast.error('Enter a referral code'); return; }
    setApplyingReferral(true);
    try {
      const { data } = await api.post('/referral/apply', { code: referralInput.trim() });
      toast.success(data.message);
      setReferralInput('');
      await refreshUser();
      loadReferral();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setApplyingReferral(false); }
  };

  const copyReferralCode = () => {
    navigator.clipboard?.writeText(referralCode);
    toast.success('Referral code copied!');
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
      <div className="flex items-center gap-3 mb-5">
        <Gift weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
        <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Referral Program</h2>
      </div>
      <p className="text-sm text-[#64748B] mb-4">Share your code with a friend. When they sign up and apply it, both of you get 1 month of Standard plan free!</p>
      {referralCode && (
        <div className="mb-5">
          <Label className="text-sm text-[#0F172A]">Your Referral Code</Label>
          <div className="flex items-center gap-2 mt-1.5">
            <div className="flex-1 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl px-4 py-2.5 font-mono text-base text-[#0F172A] tracking-wider" data-testid="referral-code-display">{referralCode}</div>
            <Button variant="outline" onClick={copyReferralCode} className="rounded-xl border-[#E2E8F0] px-3" data-testid="copy-referral-code-btn"><Copy className="w-4 h-4" /></Button>
          </div>
          <div className="flex gap-4 mt-3">
            <div className="flex items-center gap-1.5 text-sm text-[#64748B]"><UserPlus className="w-4 h-4" /> {referralStats.total_referrals} referred</div>
            <div className="flex items-center gap-1.5 text-sm text-[#10B981]"><Check weight="bold" className="w-4 h-4" /> {referralStats.successful_referrals} successful</div>
          </div>
        </div>
      )}
      {!user?.referred_by && (
        <>
          <Separator className="my-4" />
          <Label className="text-sm text-[#0F172A]">Have a referral code?</Label>
          <div className="flex items-center gap-2 mt-1.5">
            <Input value={referralInput} onChange={e => setReferralInput(e.target.value)} placeholder="Enter referral code"
              className="rounded-xl border-[#E2E8F0] bg-[#F8FAFC] font-mono uppercase" data-testid="referral-input" />
            <Button onClick={handleApplyReferral} disabled={applyingReferral} data-testid="apply-referral-btn"
              className="rounded-xl bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-5">
              {applyingReferral ? 'Applying...' : 'Apply'}
            </Button>
          </div>
        </>
      )}
      {user?.referred_by && (
        <div className="mt-3 text-sm text-[#10B981] flex items-center gap-1.5">
          <Check weight="bold" className="w-4 h-4" /> Referral code applied: {user.referred_by}
        </div>
      )}
    </div>
  );
}
