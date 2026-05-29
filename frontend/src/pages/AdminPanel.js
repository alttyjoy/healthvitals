import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { VITAL_MAP } from '@/lib/vitals';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
  Users, ChartLine, CreditCard, FileArrowDown, ShieldCheck
} from '@phosphor-icons/react';
import { UserManagement } from '@/components/admin/UserManagement';
import { CouponManagement } from '@/components/admin/CouponManagement';
import { AdminSettings } from '@/components/admin/AdminSettings';
import { ContentManagement } from '@/components/admin/ContentManagement';

export default function AdminPanel() {
  const [tab, setTab] = useState('overview');
  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadDashboard(); }, []);

  const loadDashboard = async () => {
    try {
      const [dashRes, usersRes] = await Promise.all([
        api.get('/admin/dashboard'),
        api.get('/admin/users?limit=20'),
      ]);
      setDashboard(dashRes.data);
      setUsers(usersRes.data.users || []);
      setUsersTotal(usersRes.data.total || 0);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadAnalytics = async () => {
    try {
      const res = await api.get('/admin/analytics');
      setAnalytics(res.data);
    } catch (e) { console.error(e); }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps -- lazy-load analytics once
  useEffect(() => { if (tab === 'analytics' && !analytics) loadAnalytics(); }, [tab, analytics]);

  if (loading) return (
    <div className="space-y-4 animate-pulse">{[1,2,3,4].map(i => <div key={i} className="h-24 bg-[#E2E8F0] rounded-2xl" />)}</div>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in-up" data-testid="admin-panel">
      <div className="flex items-center gap-3">
        <ShieldCheck weight="duotone" className="w-7 h-7 text-[#0EA5E9]" />
        <div>
          <h1 className="text-2xl font-medium text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>Admin Panel</h1>
          <p className="text-sm text-[#64748B]">Manage users, plans, and platform analytics</p>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="bg-white border border-[#E2E8F0] rounded-xl p-1 flex-wrap">
          <TabsTrigger value="overview" data-testid="admin-tab-overview" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Overview</TabsTrigger>
          <TabsTrigger value="users" data-testid="admin-tab-users" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Users</TabsTrigger>
          <TabsTrigger value="analytics" data-testid="admin-tab-analytics" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Analytics</TabsTrigger>
          <TabsTrigger value="content" data-testid="admin-tab-content" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Content</TabsTrigger>
          <TabsTrigger value="coupons" data-testid="admin-tab-coupons" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Coupons</TabsTrigger>
          <TabsTrigger value="settings" data-testid="admin-tab-settings" className="rounded-lg text-xs sm:text-sm data-[state=active]:bg-[#0EA5E9] data-[state=active]:text-white">Settings</TabsTrigger>
        </TabsList>

        {/* Overview */}
        <TabsContent value="overview" className="space-y-6 mt-4">
          {dashboard && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <AdminStat icon={Users} label="Total Users" value={dashboard.total_users} />
                <AdminStat icon={CreditCard} label="MRR" value={`₹${dashboard.mrr?.toLocaleString()}`} />
                <AdminStat icon={ChartLine} label="Total Entries" value={dashboard.total_entries?.toLocaleString()} />
                <AdminStat icon={FileArrowDown} label="Exports" value={dashboard.total_exports} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5">
                  <p className="text-xs text-[#64748B] uppercase tracking-wide mb-2">Plan Distribution</p>
                  <div className="space-y-3">
                    <PlanBar label="Free" count={dashboard.free_users} total={dashboard.total_users} color="#64748B" />
                    <PlanBar label="Standard" count={dashboard.standard_users} total={dashboard.total_users} color="#0EA5E9" />
                    <PlanBar label="Premium" count={dashboard.premium_users} total={dashboard.total_users} color="#EF4444" />
                  </div>
                </div>
                <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 md:col-span-2">
                  <p className="text-xs text-[#64748B] uppercase tracking-wide mb-3">Most Tracked Vitals</p>
                  <div className="space-y-2">
                    {Object.entries(dashboard.vital_usage || {}).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([key, count]) => (
                      <div key={key} className="flex items-center justify-between py-1">
                        <span className="text-sm text-[#0F172A]">{VITAL_MAP[key]?.name || key}</span>
                        <Badge className="bg-[#F8FAFC] text-[#64748B] border border-[#E2E8F0] text-xs">{count} entries</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5">
                <p className="text-xs text-[#64748B] uppercase tracking-wide mb-1">Revenue Metrics</p>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div><p className="text-2xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>₹{dashboard.mrr?.toLocaleString()}</p><p className="text-xs text-[#64748B]">Monthly Recurring Revenue</p></div>
                  <div><p className="text-2xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>₹{dashboard.arr?.toLocaleString()}</p><p className="text-xs text-[#64748B]">Annual Recurring Revenue</p></div>
                </div>
              </div>
            </>
          )}
        </TabsContent>

        {/* Users */}
        <TabsContent value="users" className="mt-4">
          <UserManagement users={users} usersTotal={usersTotal} onRefresh={loadDashboard} />
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="space-y-6 mt-4">
          {analytics ? (
            <>
              <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6">
                <h3 className="text-base font-medium text-[#0F172A] mb-4" style={{ fontFamily: 'Outfit' }}>Daily Entries (Last 30 Days)</h3>
                {analytics.daily_entries?.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={analytics.daily_entries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                      <XAxis dataKey="date" fontSize={10} tick={{ fill: '#64748B' }} tickFormatter={v => v.slice(5)} />
                      <YAxis fontSize={10} tick={{ fill: '#64748B' }} />
                      <Tooltip contentStyle={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: 12 }} />
                      <Bar dataKey="count" fill="#0EA5E9" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <p className="text-sm text-[#64748B] text-center py-8">No entry data yet</p>}
              </div>
              <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6">
                <h3 className="text-base font-medium text-[#0F172A] mb-4" style={{ fontFamily: 'Outfit' }}>Recent Audit Logs</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {(analytics.audit_logs || []).map((log, i) => (
                    <div key={`${log.action}-${log.created_at}-${i}`} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-[#F8FAFC] text-sm">
                      <span className="text-[#0F172A]">{log.action}</span>
                      <span className="text-xs text-[#64748B]">{log.created_at ? new Date(log.created_at).toLocaleString() : ''}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="animate-pulse space-y-4">{[1,2].map(i => <div key={i} className="h-64 bg-[#E2E8F0] rounded-2xl" />)}</div>
          )}
        </TabsContent>

        {/* Content Management */}
        <TabsContent value="content" className="mt-4">
          <ContentManagement />
        </TabsContent>

        {/* Coupons Management */}
        <TabsContent value="coupons" className="mt-4">
          <CouponManagement />
        </TabsContent>

        {/* Settings (SMTP + Reminders) */}
        <TabsContent value="settings" className="mt-4">
          <AdminSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function AdminStat({ icon: Icon, label, value }) {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-2">
        <Icon weight="duotone" className="w-5 h-5 text-[#0EA5E9]" />
        <span className="text-xs text-[#64748B] uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-semibold text-[#0F172A]" style={{ fontFamily: 'Outfit' }}>{value}</p>
    </div>
  );
}

function PlanBar({ label, count, total, color }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-[#0F172A]">{label}</span>
        <span className="text-[#64748B]">{count}</span>
      </div>
      <div className="h-2 bg-[#F8FAFC] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}
