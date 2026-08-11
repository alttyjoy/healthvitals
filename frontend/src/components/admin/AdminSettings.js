import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Envelope, Bell, Clock, CreditCard, Eye, EyeSlash } from '@phosphor-icons/react';

export function AdminSettings() {
  const [smtp, setSmtp] = useState({ smtp_host: '', smtp_port: 587, smtp_username: '', smtp_password: '', smtp_from_email: '', smtp_from_name: '', smtp_use_tls: true });
  const [smtpSaving, setSmtpSaving] = useState(false);
  const [reminderSettings, setReminderSettings] = useState({ enabled: false, time: '09:00' });
  const [reminderSaving, setReminderSaving] = useState(false);
  const [payment, setPayment] = useState({
    razorpay_key_id: '', razorpay_key_secret: '',
    payu_merchant_key: '', payu_merchant_salt: '',
    payu_base_url: 'https://test.payu.in/_payment',
    razorpay_configured: false, payu_configured: false,
  });
  const [paymentSaving, setPaymentSaving] = useState(false);
  const [showSecrets, setShowSecrets] = useState({ rzpSecret: false, payuSalt: false });

  useEffect(() => {
    api.get('/admin/smtp-settings').then(({ data }) => setSmtp(prev => ({ ...prev, ...data }))).catch(e => console.error('SMTP load:', e?.message));
    api.get('/admin/reminder-settings').then(({ data }) => setReminderSettings({ enabled: data.enabled || false, time: data.time || '09:00' })).catch(e => console.error('Reminder load:', e?.message));
    api.get('/admin/payment-settings').then(({ data }) => setPayment(prev => ({ ...prev, ...data }))).catch(e => console.error('Payment load:', e?.message));
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

  const savePayment = async () => {
    setPaymentSaving(true);
    try {
      await api.put('/admin/payment-settings', payment);
      toast.success('Payment gateway settings saved');
      const { data } = await api.get('/admin/payment-settings');
      setPayment(prev => ({ ...prev, ...data }));
    }
    catch (err) { toast.error(formatApiError(err)); }
    finally { setPaymentSaving(false); }
  };

  return (
    <div className="space-y-6">
      {/* Payment Gateway Settings */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6" data-testid="admin-payment-settings">
        <div className="flex items-center gap-3 mb-5">
          <CreditCard weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <div>
            <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Payment Gateways</h3>
            <p className="text-xs text-[#64748B]">Configure Razorpay and PayU.In API keys for accepting payments</p>
          </div>
        </div>

        {/* Razorpay */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <h4 className="text-sm font-medium text-[#0F172A]">Razorpay</h4>
            <Badge className={`text-[10px] px-1.5 py-0 border-0 ${payment.razorpay_configured ? 'bg-emerald-50 text-emerald-600' : 'bg-[#F1F5F9] text-[#94A3B8]'}`}>
              {payment.razorpay_configured ? 'Configured' : 'Not set'}
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm text-[#0F172A]">Key ID</Label>
              <Input value={payment.razorpay_key_id || ''} onChange={e => setPayment(s => ({ ...s, razorpay_key_id: e.target.value }))}
                placeholder="rzp_live_xxxxxxxx" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] font-mono text-sm" data-testid="razorpay-key-id" />
            </div>
            <div>
              <Label className="text-sm text-[#0F172A]">Key Secret</Label>
              <div className="relative mt-1.5">
                <Input type={showSecrets.rzpSecret ? 'text' : 'password'} value={payment.razorpay_key_secret || ''} onChange={e => setPayment(s => ({ ...s, razorpay_key_secret: e.target.value }))}
                  placeholder="Enter secret key" className="rounded-xl border-[#E2E8F0] bg-[#F8FAFC] font-mono text-sm pr-10" data-testid="razorpay-key-secret" />
                <button type="button" onClick={() => setShowSecrets(s => ({ ...s, rzpSecret: !s.rzpSecret }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B]">
                  {showSecrets.rzpSecret ? <EyeSlash className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* PayU */}
        <div className="mb-5 pt-5 border-t border-[#E2E8F0]">
          <div className="flex items-center gap-2 mb-3">
            <h4 className="text-sm font-medium text-[#0F172A]">PayU.In</h4>
            <Badge className={`text-[10px] px-1.5 py-0 border-0 ${payment.payu_configured ? 'bg-emerald-50 text-emerald-600' : 'bg-[#F1F5F9] text-[#94A3B8]'}`}>
              {payment.payu_configured ? 'Configured' : 'Not set'}
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm text-[#0F172A]">Merchant Key</Label>
              <Input value={payment.payu_merchant_key || ''} onChange={e => setPayment(s => ({ ...s, payu_merchant_key: e.target.value }))}
                placeholder="Your merchant key" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] font-mono text-sm" data-testid="payu-merchant-key" />
            </div>
            <div>
              <Label className="text-sm text-[#0F172A]">Merchant Salt</Label>
              <div className="relative mt-1.5">
                <Input type={showSecrets.payuSalt ? 'text' : 'password'} value={payment.payu_merchant_salt || ''} onChange={e => setPayment(s => ({ ...s, payu_merchant_salt: e.target.value }))}
                  placeholder="Enter salt key" className="rounded-xl border-[#E2E8F0] bg-[#F8FAFC] font-mono text-sm pr-10" data-testid="payu-merchant-salt" />
                <button type="button" onClick={() => setShowSecrets(s => ({ ...s, payuSalt: !s.payuSalt }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B]">
                  {showSecrets.payuSalt ? <EyeSlash className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="md:col-span-2">
              <Label className="text-sm text-[#0F172A]">PayU Base URL</Label>
              <Input value={payment.payu_base_url || ''} onChange={e => setPayment(s => ({ ...s, payu_base_url: e.target.value }))}
                placeholder="https://secure.payu.in/_payment" className="mt-1.5 rounded-xl border-[#E2E8F0] bg-[#F8FAFC] text-sm" data-testid="payu-base-url" />
              <p className="text-[10px] text-[#94A3B8] mt-1">Test: https://test.payu.in/_payment &nbsp;|&nbsp; Live: https://secure.payu.in/_payment</p>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end pt-4 border-t border-[#E2E8F0]">
          <Button onClick={savePayment} disabled={paymentSaving} data-testid="save-payment-btn"
            className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
            {paymentSaving ? 'Saving...' : 'Save Payment Settings'}
          </Button>
        </div>
      </div>

      {/* Reminder Settings */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6" data-testid="admin-reminder-settings">
        <div className="flex items-center gap-3 mb-5">
          <Bell weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <div>
            <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Email Reminders</h3>
            <p className="text-xs text-[#64748B]">Send daily email reminders to users who have not logged vitals</p>
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
