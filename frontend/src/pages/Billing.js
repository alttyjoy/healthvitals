import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useSearchParams } from 'react-router-dom';
import api, { formatApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Check, Star, CreditCard, ArrowUp, ArrowDown, Lightning } from '@phosphor-icons/react';

export default function Billing() {
  const { user, refreshUser } = useAuth();
  const { t } = useTheme();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [changing, setChanging] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    api.get('/plans').then(res => { setPlans(res.data || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  // Handle PayU callback via URL params
  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    const txnid = searchParams.get('txnid');
    if (paymentStatus && txnid) {
      if (paymentStatus === 'success') {
        toast.success('Payment successful! Your plan has been upgraded.');
        refreshUser();
      } else {
        toast.error('Payment failed or was cancelled. Please try again.');
      }
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, setSearchParams, refreshUser]);

  const currentPlan = user?.plan || 'free';
  const planOrder = ['free', 'standard', 'premium'];

  const handleRazorpayPayment = useCallback(async (planKey) => {
    setChanging(planKey);
    try {
      const { data: orderData } = await api.post('/razorpay/create-order', { plan_key: planKey, billing_cycle: 'monthly' });

      if (!window.Razorpay) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://checkout.razorpay.com/v1/checkout.js';
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }

      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'VitalTrack',
        description: `${orderData.plan.name} Plan - Monthly`,
        order_id: orderData.order_id,
        handler: async (response) => {
          try {
            await api.post('/razorpay/verify-payment', {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              plan_key: planKey,
            });
            await refreshUser();
            toast.success(`Successfully upgraded to ${orderData.plan.name} plan!`);
          } catch (err) {
            toast.error(formatApiError(err));
          } finally { setChanging(null); }
        },
        modal: {
          ondismiss: () => { setChanging(null); toast.info('Payment cancelled'); }
        },
        prefill: { name: user?.name || '', email: user?.email || '' },
        theme: { color: '#2D4A3E' },
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', (response) => {
        toast.error('Payment failed: ' + (response.error?.description || 'Unknown error'));
        setChanging(null);
      });
      rzp.open();
    } catch (err) {
      toast.error(formatApiError(err));
      setChanging(null);
    }
  }, [user, refreshUser]);

  const handlePayUPayment = useCallback(async (planKey) => {
    setChanging(planKey);
    try {
      const { data } = await api.post('/payu/initiate', { plan_key: planKey, billing_cycle: 'monthly' });
      // PayU requires a form POST to the payment URL
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = data.payment_url;
      Object.entries(data.form_data).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      document.body.appendChild(form);
      form.submit();
    } catch (err) {
      toast.error(formatApiError(err));
      setChanging(null);
    }
  }, []);

  const [paymentGateway, setPaymentGateway] = useState('razorpay');

  const handleChangePlan = async (planKey) => {
    if (planKey === currentPlan) return;
    const targetPlan = plans.find(p => p.key === planKey);

    if (targetPlan && targetPlan.price === 0) {
      setChanging(planKey);
      try {
        await api.post('/subscription/change', { plan_key: planKey });
        await refreshUser();
        toast.success('Plan changed to Free');
      } catch (err) {
        toast.error(formatApiError(err));
      } finally { setChanging(null); }
      return;
    }

    if (paymentGateway === 'payu') {
      handlePayUPayment(planKey);
    } else {
      handleRazorpayPayment(planKey);
    }
  };

  if (loading) return <div className="animate-pulse space-y-4">{[1,2,3].map(i => <div key={i} className="h-48 bg-[#EAE7E1] rounded-2xl" />)}</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in-up" data-testid="billing-page">
      <div>
        <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>{t('subscription_billing')}</h1>
        <p className="text-sm text-[#6E6E6A]">Manage your subscription plan</p>
      </div>

      {/* Current Plan */}
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-[#6E6E6A] uppercase tracking-wide">{t('current_plan')}</p>
            <h2 className="text-xl font-medium text-[#2C2C2A] mt-1" style={{ fontFamily: 'Outfit' }}>
              {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)}
            </h2>
            <p className="text-sm text-[#6E6E6A] mt-1">
              {user?.enabled_vitals?.length || 0} vitals enabled of {plans.find(p => p.key === currentPlan)?.vital_limit || 2} allowed
            </p>
          </div>
          <Badge className="bg-[#2D4A3E]/10 text-[#2D4A3E] border-0 text-sm px-3 py-1">
            <CreditCard weight="duotone" className="w-4 h-4 mr-1" /> Active
          </Badge>
        </div>
      </div>

      {/* Payment Gateway Selector */}
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        <p className="text-xs text-[#6E6E6A] uppercase tracking-wide mb-3">Payment Method</p>
        <div className="flex gap-3" data-testid="payment-gateway-selector">
          <button
            onClick={() => setPaymentGateway('razorpay')}
            data-testid="gateway-razorpay"
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 text-sm font-medium transition-all ${
              paymentGateway === 'razorpay'
                ? 'border-[#2D4A3E] bg-[#2D4A3E]/5 text-[#2D4A3E]'
                : 'border-[#EAE7E1] text-[#6E6E6A] hover:border-[#2D4A3E]/30'
            }`}
          >
            <CreditCard weight="duotone" className="w-5 h-5" />
            Razorpay
          </button>
          <button
            onClick={() => setPaymentGateway('payu')}
            data-testid="gateway-payu"
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 text-sm font-medium transition-all ${
              paymentGateway === 'payu'
                ? 'border-[#2D4A3E] bg-[#2D4A3E]/5 text-[#2D4A3E]'
                : 'border-[#EAE7E1] text-[#6E6E6A] hover:border-[#2D4A3E]/30'
            }`}
          >
            <Lightning weight="duotone" className="w-5 h-5" />
            PayU
          </button>
        </div>
      </div>

      {/* Plan Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map(plan => {
          const isCurrent = plan.key === currentPlan;
          const currentIdx = planOrder.indexOf(currentPlan);
          const targetIdx = planOrder.indexOf(plan.key);
          const isUpgrade = targetIdx > currentIdx;
          const isDowngrade = targetIdx < currentIdx;
          const isPopular = plan.key === 'standard';
          const isProcessing = changing === plan.key;
          return (
            <div key={plan.key}
              data-testid={`billing-plan-${plan.key}`}
              className={`relative bg-white border rounded-2xl p-6 transition-all duration-300 hover:-translate-y-0.5 ${isCurrent ? 'border-[#2D4A3E] ring-2 ring-[#2D4A3E]/10' : isPopular ? 'border-[#2D4A3E]/30' : 'border-[#EAE7E1]'}`}>
              {isPopular && !isCurrent && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-[#2D4A3E] text-white border-0 rounded-full px-3 py-0.5 text-xs">
                    <Star weight="fill" className="w-3 h-3 mr-1" /> Popular
                  </Badge>
                </div>
              )}
              {isCurrent && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-[#588157] text-white border-0 rounded-full px-3 py-0.5 text-xs">Current Plan</Badge>
                </div>
              )}
              <h3 className="text-lg font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>{plan.name}</h3>
              <div className="flex items-baseline gap-1 mt-2 mb-1">
                <span className="text-3xl font-semibold text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>
                  {plan.price === 0 ? 'Free' : `₹${plan.price}`}
                </span>
                {plan.price > 0 && <span className="text-sm text-[#6E6E6A]">/month</span>}
              </div>
              {plan.price_yearly > 0 && (
                <p className="text-xs text-[#6E6E6A] mb-4">or ₹{plan.price_yearly}/year (save {Math.round((1 - plan.price_yearly / (plan.price * 12)) * 100)}%)</p>
              )}
              <p className="text-sm text-[#6E6E6A] mb-4">Track up to {plan.vital_limit} vitals</p>
              <ul className="space-y-2 mb-6">
                {(plan.features || []).map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-[#2C2C2A]">
                    <Check weight="bold" className="w-4 h-4 text-[#588157] mt-0.5 flex-shrink-0" /> {f}
                  </li>
                ))}
              </ul>
              {isCurrent ? (
                <Button disabled className="w-full rounded-full bg-[#EAE7E1] text-[#6E6E6A]">{t('current_plan')}</Button>
              ) : (
                <Button onClick={() => handleChangePlan(plan.key)} disabled={!!changing}
                  data-testid={`billing-select-${plan.key}`}
                  className={`w-full rounded-full transition-all ${isUpgrade ? 'bg-[#2D4A3E] hover:bg-[#1E332A] text-white' : 'bg-[#EAE7E1] hover:bg-[#DEDCD5] text-[#2C2C2A]'}`}>
                  {isProcessing ? (
                    <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> Processing...</span>
                  ) : isUpgrade ? (
                    <><ArrowUp className="w-4 h-4 mr-1" /> {t('upgrade')}</>
                  ) : (
                    <><ArrowDown className="w-4 h-4 mr-1" /> {t('downgrade')}</>
                  )}
                </Button>
              )}
            </div>
          );
        })}
      </div>

      {/* Gateway Info */}
      <div className="bg-[#2D4A3E] rounded-2xl p-6 text-center text-white">
        <Lightning weight="duotone" className="w-8 h-8 mx-auto mb-3 text-white/80" />
        <h3 className="text-base font-medium mb-1" style={{ fontFamily: 'Outfit' }}>
          Secure Payments via {paymentGateway === 'payu' ? 'PayU' : 'Razorpay'}
        </h3>
        <p className="text-sm text-white/70 max-w-md mx-auto">
          All payments are processed securely through {paymentGateway === 'payu' ? 'PayU' : 'Razorpay'}. Your card details are never stored on our servers.
        </p>
      </div>
    </div>
  );
}
