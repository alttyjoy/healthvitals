import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api, { formatApiError } from '@/lib/api';
import { VITAL_TYPES, VITAL_MAP } from '@/lib/vitals';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { User, Lock, Heartbeat, Gear } from '@phosphor-icons/react';

export default function Settings() {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [enabledVitals, setEnabledVitals] = useState([]);
  const [vitalLimit, setVitalLimit] = useState(2);
  const [togglingVital, setTogglingVital] = useState(null);

  useEffect(() => {
    api.get('/vitals/enabled').then(res => {
      setEnabledVitals(res.data.enabled_vitals || []);
      setVitalLimit(res.data.vital_limit || 2);
    }).catch(() => {});
  }, []);

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      await api.put('/profile', { name });
      await refreshUser();
      toast.success('Profile updated');
    } catch (err) {
      toast.error(formatApiError(err));
    } finally { setSaving(false); }
  };

  const handleToggleVital = async (vk, enabled) => {
    setTogglingVital(vk);
    try {
      const res = await api.post('/vitals/toggle', { vital_key: vk, enabled });
      setEnabledVitals(res.data.enabled_vitals);
      await refreshUser();
      toast.success(res.data.message);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally { setTogglingVital(null); }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in-up" data-testid="settings-page">
      <div>
        <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Settings</h1>
        <p className="text-sm text-[#6E6E6A]">Manage your profile and vital preferences</p>
      </div>

      {/* Profile */}
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        <div className="flex items-center gap-3 mb-5">
          <User weight="duotone" className="w-5 h-5 text-[#2D4A3E]" />
          <h2 className="text-lg font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Profile</h2>
        </div>
        <div className="space-y-4">
          <div>
            <Label className="text-sm text-[#2C2C2A]">Full Name</Label>
            <Input value={name} onChange={e => setName(e.target.value)} data-testid="settings-name-input"
              className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9] focus:ring-[#2D4A3E]/20 focus:border-[#2D4A3E]" />
          </div>
          <div>
            <Label className="text-sm text-[#2C2C2A]">Email</Label>
            <Input value={user?.email || ''} disabled className="mt-1.5 rounded-xl border-[#EAE7E1] bg-[#FAFAF9] opacity-60" />
          </div>
          <div className="flex items-center gap-3">
            <Badge className="bg-[#2D4A3E]/10 text-[#2D4A3E] border-0">
              {user?.plan?.charAt(0).toUpperCase() + user?.plan?.slice(1)} Plan
            </Badge>
            <Badge className="bg-[#EAE7E1] text-[#6E6E6A] border-0">{user?.role}</Badge>
          </div>
          <Button onClick={handleSaveProfile} disabled={saving} data-testid="settings-save-profile-btn"
            className="rounded-full bg-[#2D4A3E] hover:bg-[#1E332A] text-white px-6">
            {saving ? 'Saving...' : 'Save Profile'}
          </Button>
        </div>
      </div>

      {/* Vital Management */}
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <Heartbeat weight="duotone" className="w-5 h-5 text-[#2D4A3E]" />
            <h2 className="text-lg font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Manage Vitals</h2>
          </div>
          <Badge className="bg-[#FAFAF9] text-[#6E6E6A] border border-[#EAE7E1]">
            {enabledVitals.length} / {vitalLimit} enabled
          </Badge>
        </div>
        <p className="text-sm text-[#6E6E6A] mb-4">
          Your {user?.plan} plan allows up to {vitalLimit} vitals. Toggle the ones you want to track.
        </p>
        <div className="space-y-1">
          {VITAL_TYPES.map(vital => {
            const isEnabled = enabledVitals.includes(vital.key);
            const isAtLimit = !isEnabled && enabledVitals.length >= vitalLimit;
            return (
              <div key={vital.key} className={`flex items-center justify-between py-3 px-4 rounded-xl transition-colors ${isEnabled ? 'bg-[#2D4A3E]/[0.03]' : 'hover:bg-[#FAFAF9]'}`}>
                <div className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: vital.color }} />
                  <div>
                    <span className="text-sm font-medium text-[#2C2C2A]">{vital.name}</span>
                    <span className="text-xs text-[#6E6E6A] ml-2">{vital.unit}</span>
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
          <p className="text-xs text-[#D96C4E] mt-3">
            You've reached your plan limit. Upgrade to enable more vitals.
          </p>
        )}
      </div>
    </div>
  );
}
