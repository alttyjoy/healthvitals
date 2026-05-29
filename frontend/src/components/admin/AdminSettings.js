import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Envelope, Bell, Clock } from '@phosphor-icons/react';

export function AdminSettings() {
  const [smtp, setSmtp] = useState({ smtp_host: '', smtp_port: 587, smtp_username: '', smtp_password: '', smtp_from_email: '', smtp_from_name: '', smtp_use_tls: true });
  const [smtpSaving, setSmtpSaving] = useState(false);
  const [reminderSettings, setReminderSettings] = useState({ enabled: false, time: '09:00' });
  const [reminderSaving, setReminderSaving] = useState(false);

  useEffect(() => {
    api.get('/admin/smtp-settings').then(({ data }) => setSmtp(prev => ({ ...prev, ...data }))).catch(e => console.error('SMTP load:', e?.message));
    api.get('/admin/reminder-settings').then(({ data }) => setReminderSettings({ enabled: data.enabled || false, time: data.time || '09:00' })).catch(e => console.error('Reminder load:', e?.message));
  }, []);

  const saveSmtp = async () => {
    setSmtpSaving(true);
    try { await api.put('/admin/smtp-settings', smtp); toast.success('SMTP settings saved'); }
    catch (err) { toast.error(formatApiError(err)); } finally { setSmtpSaving(false); }
  };

  const saveReminderSettings = async () => {
    setReminderSaving(true);
    try { await api.put('/admin/reminder-settings', reminderSettings); toast.success(`Reminders ${reminderSettings.enabled ? 'enabled' : 'disabled'}`); }
    catch (err) { toast.error(formatApiError(err)); } finally { setReminderSaving(false); }
  };

  const triggerReminders = async () => {
    try { await api.post('/admin/send-reminders'); toast.success('Reminder check completed'); }
    catch (err) { toast.error(formatApiError(err)); }
  };

  return (
    <div className="space-y-6">
      {/* Reminder Settings */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6" data-testid="admin-reminder-settings">
        <div className="flex items-center gap-3 mb-5">
          <Bell weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <div>
            <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Email Reminders</h3>
            <p className="text-xs text-[#64748B]">Send daily email reminders to users who haven't logged vitals</p>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <Switch checked={reminderSettings.enabled} onCheckedChange={v => setReminderSettings(s => ({ ...s, enabled: v }))} data-testid="reminder-enabled-toggle" />
            <Label className="text-sm text-[#0F172A]">Enable daily reminders</Label>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#64748B]" />
            <Input type="time" value={reminderSettings.time} onChange={e => setReminderSettings(s => ({ ...s, time: e.target.value }))} className="rounded-xl border-[#E2E8F0] w-32" data-testid="reminder-time-input" />
          </div>
        </div>
        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-[#E2E8F0]">
          <Button onClick={saveReminderSettings} disabled={reminderSaving} data-testid="save-reminder-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6 text-sm">
            {reminderSaving ? 'Saving...' : 'Save Schedule'}
          </Button>
          <Button variant="outline" onClick={triggerReminders} data-testid="trigger-reminders-btn" className="rounded-full border-[#E2E8F0] text-sm">Send Now</Button>
        </div>
      </div>
      {/* SMTP Config */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6" data-testid="admin-smtp-form">
        <div className="flex items-center gap-3 mb-5">
          <Envelope weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <div>
            <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>SMTP Configuration</h3>
            <p className="text-xs text-[#64748B]">Configure email settings for reminders and notifications</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><Label className="text-sm text-[#0F172A]">SMTP Host</Label><Input value={smtp.smtp_host || ''} onChange={e => setSmtp(s => ({ ...s, smtp_host: e.target.value }))} placeholder="smtp.gmail.com" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-host" /></div>
          <div><Label className="text-sm text-[#0F172A]">SMTP Port</Label><Input type="number" value={smtp.smtp_port || ''} onChange={e => setSmtp(s => ({ ...s, smtp_port: parseInt(e.target.value) || 0 }))} placeholder="587" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-port" /></div>
          <div><Label className="text-sm text-[#0F172A]">Username</Label><Input value={smtp.smtp_username || ''} onChange={e => setSmtp(s => ({ ...s, smtp_username: e.target.value }))} placeholder="your@email.com" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-username" /></div>
          <div><Label className="text-sm text-[#0F172A]">Password</Label><Input type="password" value={smtp.smtp_password || ''} onChange={e => setSmtp(s => ({ ...s, smtp_password: e.target.value }))} placeholder="App password" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-password" /></div>
          <div><Label className="text-sm text-[#0F172A]">From Email</Label><Input value={smtp.smtp_from_email || ''} onChange={e => setSmtp(s => ({ ...s, smtp_from_email: e.target.value }))} placeholder="noreply@vitaltrack.in" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-from-email" /></div>
          <div><Label className="text-sm text-[#0F172A]">From Name</Label><Input value={smtp.smtp_from_name || ''} onChange={e => setSmtp(s => ({ ...s, smtp_from_name: e.target.value }))} placeholder="VitalTrack" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC]" data-testid="smtp-from-name" /></div>
        </div>
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#E2E8F0]">
          <div className="flex items-center gap-3">
            <Switch checked={smtp.smtp_use_tls !== false} onCheckedChange={v => setSmtp(s => ({ ...s, smtp_use_tls: v }))} data-testid="smtp-tls-toggle" />
            <Label className="text-sm text-[#0F172A]">Use TLS</Label>
          </div>
          <Button onClick={saveSmtp} disabled={smtpSaving} data-testid="smtp-save-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
            {smtpSaving ? 'Saving...' : 'Save SMTP Settings'}
          </Button>
        </div>
      </div>
    </div>
  );
}
