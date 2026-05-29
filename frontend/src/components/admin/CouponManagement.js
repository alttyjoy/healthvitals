import { useState, useEffect } from 'react';
import api, { formatApiError } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tag, Trash, PencilSimple, Plus } from '@phosphor-icons/react';

export function CouponManagement() {
  const [coupons, setCoupons] = useState([]);
  const [editingCoupon, setEditingCoupon] = useState(null);
  const [couponForm, setCouponForm] = useState({ code: '', discount_percent: 10, max_uses: 0, valid_plans: [], expires_at: '', active: true });
  const [couponSaving, setCouponSaving] = useState(false);

  useEffect(() => { loadCoupons(); }, []);

  const loadCoupons = async () => {
    try { const { data } = await api.get('/admin/coupons'); setCoupons(data.coupons || []); }
    catch (e) { console.error('Load coupons failed:', e?.message); }
  };

  const saveCoupon = async () => {
    if (!couponForm.code.trim() || !couponForm.discount_percent) { toast.error('Code and discount are required'); return; }
    setCouponSaving(true);
    try {
      if (editingCoupon?.isNew) { await api.post('/admin/coupons', couponForm); toast.success('Coupon created'); }
      else { await api.put(`/admin/coupons/${editingCoupon.code}`, couponForm); toast.success('Coupon updated'); }
      setEditingCoupon(null);
      loadCoupons();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setCouponSaving(false); }
  };

  const deleteCoupon = async (code) => {
    if (!window.confirm(`Delete coupon ${code}?`)) return;
    try { await api.delete(`/admin/coupons/${code}`); toast.success('Coupon deleted'); loadCoupons(); }
    catch (err) { toast.error(formatApiError(err)); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Tag weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Coupon Codes</h3>
        </div>
        <Button onClick={() => { setEditingCoupon({ isNew: true }); setCouponForm({ code: '', discount_percent: 10, max_uses: 0, valid_plans: [], expires_at: '', active: true }); }}
          data-testid="admin-add-coupon-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-4 text-sm">
          <Plus className="w-4 h-4 mr-1" /> Create Coupon
        </Button>
      </div>
      <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden overflow-x-auto">
        <table className="w-full text-sm" data-testid="admin-coupons-table">
          <thead>
            <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0]">
              <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Code</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Discount</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide hidden sm:table-cell">Usage</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide hidden sm:table-cell">Expires</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Status</th>
              <th className="text-right px-5 py-3 text-xs font-semibold text-[#0F172A] uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            {coupons.map(c => (
              <tr key={c.code} className="border-b border-[#E2E8F0] hover:bg-[#F8FAFC]">
                <td className="px-5 py-3 font-mono font-semibold text-[#0F172A]">{c.code}</td>
                <td className="px-5 py-3"><Badge className="bg-[#0EA5E9]/10 text-[#0EA5E9] border-0 text-xs font-semibold">{c.discount_percent}% off</Badge></td>
                <td className="px-5 py-3 text-[#64748B] hidden sm:table-cell">{c.used_count || 0}{c.max_uses > 0 ? ` / ${c.max_uses}` : ' (unlimited)'}</td>
                <td className="px-5 py-3 text-[#64748B] text-xs hidden sm:table-cell">{c.expires_at ? new Date(c.expires_at).toLocaleDateString() : 'Never'}</td>
                <td className="px-5 py-3"><Badge className={`border-0 text-xs ${c.active !== false ? 'bg-[#10B981]/10 text-[#10B981]' : 'bg-[#EF4444]/10 text-[#EF4444]'}`}>{c.active !== false ? 'Active' : 'Inactive'}</Badge></td>
                <td className="px-5 py-3 text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`edit-coupon-${c.code}`}
                      onClick={() => { setEditingCoupon(c); setCouponForm({ code: c.code, discount_percent: c.discount_percent, max_uses: c.max_uses || 0, valid_plans: c.valid_plans || [], expires_at: c.expires_at || '', active: c.active !== false }); }}>
                      <PencilSimple className="w-4 h-4 text-[#64748B]" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`delete-coupon-${c.code}`} onClick={() => deleteCoupon(c.code)}>
                      <Trash className="w-4 h-4 text-[#EF4444]" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
            {coupons.length === 0 && <tr><td colSpan={6} className="px-5 py-8 text-center text-[#64748B]">No coupons created yet.</td></tr>}
          </tbody>
        </table>
      </div>
      <Dialog open={!!editingCoupon} onOpenChange={(open) => { if (!open) setEditingCoupon(null); }}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle style={{ fontFamily: 'Outfit' }}>{editingCoupon?.isNew ? 'Create Coupon' : `Edit: ${editingCoupon?.code || ''}`}</DialogTitle></DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <Label className="text-sm">Coupon Code</Label>
              <Input value={couponForm.code} onChange={e => setCouponForm(f => ({ ...f, code: e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '') }))}
                placeholder="e.g. SAVE20" disabled={editingCoupon && !editingCoupon.isNew} data-testid="coupon-code-form-input" className="mt-1 rounded-xl border-[#E2E8F0] font-mono uppercase" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm">Discount (%)</Label>
                <Input type="number" min={1} max={100} value={couponForm.discount_percent}
                  onChange={e => setCouponForm(f => ({ ...f, discount_percent: Math.min(100, Math.max(1, parseInt(e.target.value) || 0)) }))}
                  data-testid="coupon-discount-input" className="mt-1 rounded-xl border-[#E2E8F0]" />
              </div>
              <div>
                <Label className="text-sm">Max Uses (0 = unlimited)</Label>
                <Input type="number" min={0} value={couponForm.max_uses} onChange={e => setCouponForm(f => ({ ...f, max_uses: parseInt(e.target.value) || 0 }))}
                  data-testid="coupon-max-uses-input" className="mt-1 rounded-xl border-[#E2E8F0]" />
              </div>
            </div>
            <div>
              <Label className="text-sm">Expiry Date (optional)</Label>
              <Input type="date" value={couponForm.expires_at ? couponForm.expires_at.split('T')[0] : ''}
                onChange={e => setCouponForm(f => ({ ...f, expires_at: e.target.value ? new Date(e.target.value).toISOString() : '' }))}
                data-testid="coupon-expiry-input" className="mt-1 rounded-xl border-[#E2E8F0]" />
            </div>
            <div className="flex items-center gap-3">
              <Switch checked={couponForm.active} onCheckedChange={v => setCouponForm(f => ({ ...f, active: v }))} data-testid="coupon-active-toggle" />
              <Label className="text-sm">Active</Label>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setEditingCoupon(null)} className="rounded-full border-[#E2E8F0]">Cancel</Button>
              <Button onClick={saveCoupon} disabled={couponSaving} data-testid="save-coupon-btn" className="rounded-full bg-[#0EA5E9] hover:bg-[#0284C7] text-white px-6">
                {couponSaving ? 'Saving...' : editingCoupon?.isNew ? 'Create Coupon' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
