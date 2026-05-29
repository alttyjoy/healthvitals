import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import api, { formatApiError } from '@/lib/api';
import { VITAL_TYPES, VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { User, Heartbeat, Gear, Moon, Globe, LinkSimple, Lock, Copy, Trash, Eye, UserPlus, Gift, Check } from '@phosphor-icons/react';

const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
];

export default function Settings() {
  const { user, refreshUser } = useAuth();
  const { darkMode, toggleDarkMode, language, setLanguage, t } = useTheme();
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [enabledVitals, setEnabledVitals] = useState([]);
  const [vitalLimit, setVitalLimit] = useState(2);
  const [togglingVital, setTogglingVital] = useState(null);
  // Shared reports
  const [sharedReports, setSharedReports] = useState([]);
  const [showCreateShare, setShowCreateShare] = useState(false);
  const [shareVitals, setShareVitals] = useState([]);
  const [shareStart, setShareStart] = useState(() => new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0]);
  const [shareEnd, setShareEnd] = useState(() => new Date().toISOString().split('T')[0]);
  const [sharePassword, setSharePassword] = useState('');
  const [shareDays, setShareDays] = useState(7);
  const [creatingShare, setCreatingShare] = useState(false);
  // Referral
  const [referralCode, setReferralCode] = useState('');
  const [referralStats, setReferralStats] = useState({ total_referrals: 0, successful_referrals: 0 });
  const [referralInput, setReferralInput] = useState('');
  const [applyingReferral, setApplyingReferral] = useState(false);

  useEffect(() => {
    api.get('/vitals/enabled').then(res => {
      setEnabledVitals(res.data.enabled_vitals || []);
      setVitalLimit(res.data.vital_limit || 2);
    }).catch(err => console.error('Failed to load vitals:', err?.message));
    loadSharedReports();
    loadReferral();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps -- runs once on mount

  const loadReferral = async () => {
    try {
      const { data } = await api.get('/referral');
      setReferralCode(data.referral_code || '');
      setReferralStats({ total_referrals: data.total_referrals || 0, successful_referrals: data.successful_referrals || 0 });
    } catch (err) { console.error('Failed to load:', err?.message); }
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

  const loadSharedReports = async () => {
    try {
      const { data } = await api.get('/shared-reports');
      setSharedReports(data || []);
    } catch (err) { console.error('Failed to load:', err?.message); }
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      await api.put('/profile', { name });
      await refreshUser();
      toast.success(t('save_profile') + ' ✓');
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setSaving(false); }
  };

  const handleToggleVital = async (vk, enabled) => {
    setTogglingVital(vk);
    try {
      const res = await api.post('/vitals/toggle', { vital_key: vk, enabled });
      setEnabledVitals(res.data.enabled_vitals);
      await refreshUser();
      toast.success(res.data.message);
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setTogglingVital(null); }
  };

  const handleCreateSharedReport = async () => {
    if (shareVitals.length === 0) { toast.error('Select at least one vital'); return; }
    setCreatingShare(true);
    try {
      const { data } = await api.post('/shared-reports', {
        vital_keys: shareVitals, start_date: shareStart, end_date: shareEnd,
        expires_days: shareDays, password: sharePassword || null,
      });
      const link = `${window.location.origin}/shared/${data.token}`;
      navigator.clipboard?.writeText(link);
      toast.success('Shared report created! Link copied to clipboard.');
      setShowCreateShare(false);
      setSharePassword('');
      setShareVitals([]);
      loadSharedReports();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setCreatingShare(false); }
  };

  const revokeShare = async (id) => {
    try {
      await api.delete(`/shared-reports/${id}`);
      toast.success('Share link revoked');
      loadSharedReports();
    } catch (err) { toast.error(formatApiError(err)); }
  };

  const copyShareLink = (token) => {
    const link = `${window.location.origin}/shared/${token}`;
    navigator.clipboard?.writeText(link);
    toast.success('Link copied!');
  };

  const plan = user?.plan || 'free';
  const canShare = plan !== 'free';

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in-up" data-testid="settings-page">
      <div>
        <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{t('settings')}</h1>
        <p className="text-sm text-[#64748B]">Manage your profile, vitals, and preferences</p>
      </div>

      {/* Profile */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        <div className="flex items-center gap-3 mb-5">
          <User weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{t('profile')}</h2>
        </div>
        <div className="space-y-4">
          <div>
            <Label className="text-sm text-[#0F172A]">{t('full_name')}</Label>
            <Input value={name} onChange={e => setName(e.target.value)} data-testid="settings-name-input"
              className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" />
          </div>
          <div>
            <Label className="text-sm text-[#0F172A]">{t('email')}</Label>
            <Input value={user?.email || ''} disabled className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] opacity-60" />
          </div>
          <div className="flex items-center gap-3">
            <Badge className="bg-[#0EA5E9]/10 text-[#0EA5E9] border-0">{plan.charAt(0).toUpperCase() + plan.slice(1)} Plan</Badge>
            <Badge className="bg-[#E2E8F0] text-[#64748B] border-0">{user?.role}</Badge>
          </div>
          <Button onClick={handleSaveProfile} disabled={saving} data-testid="settings-save-profile-btn"
            className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
            {saving ? 'Saving...' : t('save_profile')}
          </Button>
        </div>
      </div>

      {/* Preferences: Dark Mode + Language */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        <div className="flex items-center gap-3 mb-5">
          <Gear weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Preferences</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <Moon weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
              <div>
                <p className="text-sm font-medium text-[#0F172A]">{t('dark_mode')}</p>
                <p className="text-xs text-[#64748B]">Switch between light and dark theme</p>
              </div>
            </div>
            <Switch checked={darkMode} onCheckedChange={toggleDarkMode} data-testid="dark-mode-toggle" />
          </div>
          <Separator />
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <Globe weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
              <div>
                <p className="text-sm font-medium text-[#0F172A]">{t('language')}</p>
                <p className="text-xs text-[#64748B]">Choose your preferred language</p>
              </div>
            </div>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-[160px] rounded-xl border-[#E2E8F0]" data-testid="language-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map(l => (
                  <SelectItem key={l.code} value={l.code}>{l.native} ({l.name})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Vital Management */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <Heartbeat weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
            <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{t('manage_vitals')}</h2>
          </div>
          <Badge className="bg-[#F8FAFC] text-[#64748B] border border-[#E2E8F0]">
            {enabledVitals.length} / {vitalLimit} enabled
          </Badge>
        </div>
        <p className="text-sm text-[#64748B] mb-4">
          Your {plan} plan allows up to {vitalLimit} vitals. Toggle the ones you want to track.
        </p>
        <div className="space-y-1">
          {VITAL_TYPES.map(vital => {
            const isEnabled = enabledVitals.includes(vital.key);
            const isAtLimit = !isEnabled && enabledVitals.length >= vitalLimit;
            return (
              <div key={vital.key} className={`flex items-center justify-between py-3 px-4 rounded-xl transition-colors ${isEnabled ? 'bg-[#0EA5E9]/[0.03]' : 'hover:bg-[#F8FAFC]'}`}>
                <div className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: vital.color }} />
                  <div>
                    <span className="text-sm font-medium text-[#0F172A]">{vital.name}</span>
                    <span className="text-xs text-[#64748B] ml-2">{vital.unit}</span>
                  </div>
                </div>
                <Switch
                  checked={isEnabled}
                  disabled={togglingVital === vital.key || (isAtLimit && !isEnabled)}
                  onCheckedChange={(checked) => handleToggleVital(vital.key, checked)}
                  data-testid={`vital-toggle-${vital.key}`}
                />
              </div>
            );
          })}
        </div>
        {enabledVitals.length >= vitalLimit && (
          <p className="text-xs text-[#EF4444] mt-3">You've reached your plan limit. Upgrade to enable more vitals.</p>
        )}
      </div>

      {/* Shared Reports */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <LinkSimple weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
            <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{t('shared_reports')}</h2>
          </div>
          {canShare && (
            <Dialog open={showCreateShare} onOpenChange={setShowCreateShare}>
              <DialogTrigger asChild>
                <Button className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-5 text-sm" data-testid="create-shared-report-btn">
                  {t('create_shared_report')}
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle style={{ fontFamily: 'Outfit' }}>{t('create_shared_report')}</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div>
                    <Label className="text-sm">Select Vitals</Label>
                    <div className="grid grid-cols-2 gap-2 mt-2 max-h-40 overflow-y-auto">
                      {enabledVitals.map(vk => (
                        <label key={vk} className="flex items-center gap-2 text-sm cursor-pointer">
                          <Checkbox checked={shareVitals.includes(vk)} onCheckedChange={() => setShareVitals(prev => prev.includes(vk) ? prev.filter(v => v !== vk) : [...prev, vk])} />
                          {VITAL_MAP[vk]?.name || vk}
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label className="text-sm">Start Date</Label>
                      <Input type="date" value={shareStart} onChange={e => setShareStart(e.target.value)} className="mt-1 rounded-xl" />
                    </div>
                    <div>
                      <Label className="text-sm">End Date</Label>
                      <Input type="date" value={shareEnd} onChange={e => setShareEnd(e.target.value)} className="mt-1 rounded-xl" />
                    </div>
                  </div>
                  <div>
                    <Label className="text-sm flex items-center gap-1"><Lock className="w-3 h-3" /> Password (optional)</Label>
                    <Input type="password" value={sharePassword} onChange={e => setSharePassword(e.target.value)}
                      placeholder="Leave empty for no password" className="mt-1 rounded-xl" data-testid="share-password-input" />
                  </div>
                  <div>
                    <Label className="text-sm">{t('expires_in')}</Label>
                    <Select value={String(shareDays)} onValueChange={v => setShareDays(parseInt(v))}>
                      <SelectTrigger className="mt-1 rounded-xl"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 day</SelectItem>
                        <SelectItem value="7">7 days</SelectItem>
                        <SelectItem value="30">30 days</SelectItem>
                        <SelectItem value="90">90 days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleCreateSharedReport} disabled={creatingShare} data-testid="create-share-submit-btn"
                    className="w-full rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white">
                    {creatingShare ? 'Creating...' : 'Create & Copy Link'}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>

        {!canShare ? (
          <p className="text-sm text-[#64748B]">Sharing requires Standard or Premium plan. Upgrade to share reports.</p>
        ) : sharedReports.length === 0 ? (
          <p className="text-sm text-[#64748B]">No shared reports yet. Create one to share your health data securely.</p>
        ) : (
          <div className="space-y-2">
            {sharedReports.filter(r => r.active).map(report => (
              <div key={report.id} className="flex items-center justify-between py-3 px-4 rounded-xl border border-[#E2E8F0] hover:bg-[#F8FAFC]">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-[#0F172A] truncate">
                      {(report.vital_keys || []).map(vk => VITAL_MAP[vk]?.name || vk).join(', ')}
                    </span>
                    {report.has_password && <Lock className="w-3.5 h-3.5 text-[#64748B]" />}
                  </div>
                  <p className="text-xs text-[#64748B]">{report.start_date} to {report.end_date}</p>
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" onClick={() => copyShareLink(report.token)} className="h-8 w-8" data-testid={`copy-share-${report.id}`}>
                    <Copy className="w-4 h-4 text-[#64748B]" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => window.open(`/shared/${report.token}`, '_blank')} className="h-8 w-8">
                    <Eye className="w-4 h-4 text-[#64748B]" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => revokeShare(report.id)} className="h-8 w-8" data-testid={`revoke-share-${report.id}`}>
                    <Trash className="w-4 h-4 text-[#EF4444]" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Referral Program */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
        <div className="flex items-center gap-3 mb-5">
          <Gift weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Referral Program</h2>
        </div>
        <p className="text-sm text-[#64748B] mb-4">
          Share your code with a friend. When they sign up and apply it, both of you get 1 month of Standard plan free!
        </p>

        {/* Your Referral Code */}
        {referralCode && (
          <div className="mb-5">
            <Label className="text-sm text-[#0F172A]">Your Referral Code</Label>
            <div className="flex items-center gap-2 mt-1.5">
              <div className="flex-1 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl px-4 py-2.5 font-mono text-base text-[#0F172A] tracking-wider" data-testid="referral-code-display">
                {referralCode}
              </div>
              <Button variant="outline" onClick={copyReferralCode} className="rounded-xl border-[#E2E8F0] px-3" data-testid="copy-referral-code-btn">
                <Copy className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex gap-4 mt-3">
              <div className="flex items-center gap-1.5 text-sm text-[#64748B]">
                <UserPlus className="w-4 h-4" /> {referralStats.total_referrals} referred
              </div>
              <div className="flex items-center gap-1.5 text-sm text-[#10B981]">
                <Check weight="bold" className="w-4 h-4" /> {referralStats.successful_referrals} successful
              </div>
            </div>
          </div>
        )}

        {/* Apply a Referral Code */}
        {!user?.referred_by && (
          <>
            <Separator className="my-4" />
            <Label className="text-sm text-[#0F172A]">Have a referral code?</Label>
            <div className="flex items-center gap-2 mt-1.5">
              <Input
                value={referralInput}
                onChange={e => setReferralInput(e.target.value)}
                placeholder="Enter referral code"
                className="rounded-xl border-[#E2E8F0] bg-[#F8FAFC] font-mono uppercase"
                data-testid="referral-input"
              />
              <Button onClick={handleApplyReferral} disabled={applyingReferral}
                data-testid="apply-referral-btn"
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
    </div>
  );
}
