import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Receipt, ArrowLeft, ArrowRight } from '@phosphor-icons/react';

const STATUS_STYLES = {
  success: 'bg-emerald-50 text-emerald-600',
  initiated: 'bg-amber-50 text-amber-600',
  failed: 'bg-red-50 text-red-500',
};

const GATEWAY_STYLES = {
  Razorpay: 'bg-sky-50 text-sky-600',
  PayU: 'bg-violet-50 text-violet-600',
};

export function PaymentHistory() {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => { loadPayments(); }, [page]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadPayments = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/admin/payments?skip=${page * limit}&limit=${limit}`);
      setTransactions(data.transactions || []);
      setTotal(data.total || 0);
    } catch (e) { console.error('Failed to load payments:', e?.message); }
    finally { setLoading(false); }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-4" data-testid="payment-history">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Receipt weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
          <div>
            <h3 className="text-base font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Payment History</h3>
            <p className="text-xs text-[#64748B]">{total} transaction{total !== 1 ? 's' : ''} recorded</p>
          </div>
        </div>
        <Button variant="outline" onClick={loadPayments} className="rounded-full border-[#E2E8F0] text-sm" data-testid="refresh-payments-btn">
          Refresh
        </Button>
      </div>

      <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden">
        {loading ? (
          <div className="animate-pulse space-y-2 p-6">
            {[1,2,3,4,5].map(i => <div key={i} className="h-12 bg-[#F1F5F9] rounded-lg" />)}
          </div>
        ) : transactions.length === 0 ? (
          <div className="text-center py-16 text-[#64748B]">
            <Receipt weight="duotone" className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p className="text-sm">No payment transactions yet</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="hidden md:grid grid-cols-12 gap-2 px-5 py-3 bg-[#F8FAFC] border-b border-[#E2E8F0] text-[10px] text-[#64748B] uppercase tracking-wider font-medium">
              <div className="col-span-3">User</div>
              <div className="col-span-2">Gateway</div>
              <div className="col-span-2">Plan</div>
              <div className="col-span-1">Amount</div>
              <div className="col-span-2">Order ID</div>
              <div className="col-span-1">Status</div>
              <div className="col-span-1">Date</div>
            </div>
            {/* Rows */}
            {transactions.map(tx => (
              <div key={tx.id} className="grid grid-cols-1 md:grid-cols-12 gap-1 md:gap-2 px-5 py-3 border-b border-[#F1F5F9] hover:bg-[#FAFBFC] transition-colors text-sm" data-testid={`tx-row-${tx.id}`}>
                <div className="col-span-3 truncate">
                  <p className="font-medium text-[#0F172A] text-sm truncate">{tx.user_email}</p>
                  <p className="text-[10px] text-[#94A3B8] truncate md:hidden">{tx.order_id}</p>
                </div>
                <div className="col-span-2">
                  <Badge className={`text-[10px] px-1.5 py-0 border-0 ${GATEWAY_STYLES[tx.gateway] || 'bg-gray-50 text-gray-500'}`}>
                    {tx.gateway}
                  </Badge>
                </div>
                <div className="col-span-2 text-[#0F172A] capitalize">{tx.plan}</div>
                <div className="col-span-1 text-[#0F172A] tabular-nums">
                  {tx.amount != null ? `₹${tx.amount}` : '—'}
                </div>
                <div className="col-span-2 hidden md:block">
                  <span className="text-xs text-[#64748B] font-mono truncate block">{tx.order_id?.slice(0, 18)}</span>
                </div>
                <div className="col-span-1">
                  <Badge className={`text-[10px] px-1.5 py-0 border-0 capitalize ${STATUS_STYLES[tx.status] || 'bg-gray-50 text-gray-500'}`}>
                    {tx.status}
                  </Badge>
                </div>
                <div className="col-span-1 text-xs text-[#64748B]">
                  {tx.created_at ? new Date(tx.created_at).toLocaleDateString('en', { month: 'short', day: 'numeric' }) : '—'}
                </div>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-[#64748B]">Page {page + 1} of {totalPages}</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(p => p - 1)} className="rounded-lg border-[#E2E8F0]" data-testid="payments-prev-page">
              <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Prev
            </Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)} className="rounded-lg border-[#E2E8F0]" data-testid="payments-next-page">
              Next <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
