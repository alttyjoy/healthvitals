import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api, { formatApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Check, Star, CreditCard, ArrowUp, Lightning } from '@phosphor-icons/react';

export default function Billing() {
  const { user, refreshUser } = useAuth();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [changing, setChanging] = useState(false);

  useEffect(() => {
    api.get('/plans').then(res => { setPlans(res.data || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const currentPlan = user?.plan || 'free';

  const handleChangePlan = async (planKey) => {
    if (planKey === currentPlan) return;
    setChanging(true);
    try {
      await api.post('/subscription/change', { plan_key: planKey });
      await refreshUser();
      toast.success(`Plan changed to ${planKey.charAt(0).toUpperCase() + planKey.slice(1)}`);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally { setChanging(false); }
  };

  if (loading) return <div className="animate-pulse space-y-4">{[1,2,3].map(i => <div key={i} className="h-48 bg-[#EAE7E1] rounded-2xl" />)}</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in-up" data-testid="billing-page">
      <div>
        <h1 className="text-2xl font-medium text-[#2C2C2A]" style={{ fontFamily: 'Outfit' }}>Subscription & Billing</h1>
        <p className="text-sm text-[#6E6E6A]">Manage your subscription plan</p>
      </div>

      {/* Current Plan */}
      <div className="bg-white border border-[#EAE7E1] rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-[#6E6E6A] uppercase tracking-wide">Current Plan</p>
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

      {/* Plan Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map(plan => {
          const isCurrent = plan.key === currentPlan;
          const isUpgrade = plans.findIndex(p => p.key === plan.key) > plans.findIndex(p => p.key === currentPlan);
          const isDowngrade = plans.findIndex(p => p.key === plan.key) < plans.findIndex(p => p.key === currentPlan);
          const isPopular = plan.key === 'standard';
          return (
            <div key={plan.key}
              data-testid={`billing-plan-${plan.key}`}
              className={`relative bg-white border rounded-2xl p-6 transition-all duration-300 ${isCurrent ? 'border-[#2D4A3E] ring-2 ring-[#2D4A3E]/10' : isPopular ? 'border-[#2D4A3E]/30' : 'border-[#EAE7E1]'}`}>
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
                <Button disabled className="w-full rounded-full bg-[#EAE7E1] text-[#6E6E6A]">Current Plan</Button>
              ) : (
                <Button onClick={() => handleChangePlan(plan.key)} disabled={changing}
                  data-testid={`billing-select-${plan.key}`}
                  className={`w-full rounded-full ${isUpgrade ? 'bg-[#2D4A3E] hover:bg-[#1E332A] text-white' : 'bg-[#EAE7E1] hover:bg-[#DEDCD5] text-[#2C2C2A]'}`}>
                  {isUpgrade ? <><ArrowUp className="w-4 h-4 mr-1" /> Upgrade</> : 'Switch'}
                </Button>
              )}
            </div>
          );
        })}
      </div>

      {/* Payment Info */}
      <div className="bg-[#FAFAF9] border border-[#EAE7E1] rounded-2xl p-6 text-center">
        <Lightning weight="duotone" className="w-8 h-8 text-[#2D4A3E] mx-auto mb-3" />
        <h3 className="text-base font-medium text-[#2C2C2A] mb-1" style={{ fontFamily: 'Outfit' }}>Payment Gateway Integration</h3>
        <p className="text-sm text-[#6E6E6A] max-w-md mx-auto">
          Razorpay, PayU.In, and Stripe payment gateways are architecturally ready. Plan upgrades currently switch your plan instantly for demo purposes.
        </p>
      </div>
    </div>
  );
}
