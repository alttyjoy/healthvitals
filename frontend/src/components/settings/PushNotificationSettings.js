import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { BellRinging } from '@phosphor-icons/react';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
  return outputArray;
}

export function PushNotificationSettings() {
  const [supported, setSupported] = useState(false);
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);

  useEffect(() => {
    const check = async () => {
      const isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
      setSupported(isSupported);
      if (!isSupported) { setLoading(false); return; }
      try {
        const { data } = await api.get('/push/status');
        setSubscribed(data.subscribed);
      } catch (err) { console.error('Push status check:', err?.message); }
      setLoading(false);
    };
    check();
  }, []);

  const togglePush = async (enable) => {
    setToggling(true);
    try {
      if (enable) {
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') { toast.error('Notification permission denied'); setToggling(false); return; }
        const reg = await navigator.serviceWorker.register('/sw-push.js');
        await navigator.serviceWorker.ready;
        const vapidKey = process.env.REACT_APP_VAPID_PUBLIC_KEY;
        const subscription = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(vapidKey)
        });
        await api.post('/push/subscribe', { subscription: subscription.toJSON() });
        setSubscribed(true);
        toast.success('Push notifications enabled!');
      } else {
        const reg = await navigator.serviceWorker.getRegistration('/sw-push.js');
        if (reg) {
          const sub = await reg.pushManager.getSubscription();
          if (sub) {
            await api.post('/push/unsubscribe', { endpoint: sub.endpoint });
            await sub.unsubscribe();
          }
        }
        setSubscribed(false);
        toast.info('Push notifications disabled');
      }
    } catch (err) {
      console.error('Push toggle error:', err);
      toast.error('Failed to update push notifications');
    }
    setToggling(false);
  };

  if (!supported) return null;

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
      <div className="flex items-center gap-3 mb-4">
        <BellRinging weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
        <h2 className="text-lg font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Push Notifications</h2>
      </div>
      <p className="text-sm text-[#64748B] mb-4">Get browser notifications for daily tracking reminders and important updates.</p>
      {loading ? (
        <div className="h-6 w-32 bg-[#E2E8F0] rounded animate-pulse" />
      ) : (
        <div className="flex items-center gap-3">
          <Switch
            checked={subscribed}
            onCheckedChange={togglePush}
            disabled={toggling}
            data-testid="push-notification-toggle"
          />
          <Label className="text-sm text-[#0F172A]">
            {toggling ? 'Updating...' : subscribed ? 'Notifications enabled' : 'Enable push notifications'}
          </Label>
        </div>
      )}
    </div>
  );
}
